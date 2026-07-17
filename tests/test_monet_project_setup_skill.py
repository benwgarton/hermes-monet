"""Publication smoke tests for the Monet Hermes community tap."""

from __future__ import annotations

import base64
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any

import pytest

SKILL = Path(__file__).parents[1] / "skills" / "monet-project-setup"
TAP = SKILL.parents[1]
sys.path.insert(0, str(SKILL / "scripts"))

from project_primer_runtime import PrimerError, load_project_primer  # noqa: E402


def test_frontmatter_matches_hermes_contribution_contract() -> None:
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    description = re.search(r"^description: (.*)$", text, re.MULTILINE)
    author = re.search(r"^author: (.*)$", text, re.MULTILINE)
    assert description is not None
    assert len(description.group(1)) <= 60
    assert description.group(1).endswith(".")
    assert author is not None and "Benjamin Garton" in author.group(1)
    assert "commands: [python3]" in text
    assert "requires_toolsets: [terminal]" in text
    for relative in (
        "references/security.md",
        "references/pairing.md",
        "scripts/build_primer.py",
        "scripts/verify_package.py",
        "templates/example-primer.json",
        "templates/example-preview.json",
    ):
        assert (SKILL / relative).is_file(), relative

    grouping = json.loads((TAP / "skills.sh.json").read_text(encoding="utf-8"))
    assert grouping["groupings"] == [
        {
            "title": "Design Review and AI Handoffs",
            "skills": ["monet-project-setup"],
        }
    ]
    assert "MIT License" in (TAP / "LICENSE").read_text(encoding="utf-8")


def test_example_builds_and_verifies_as_secret_free(tmp_path: Path) -> None:
    build = subprocess.run(  # noqa: S603 - fixed interpreter and repository script
        [
            sys.executable,
            str(SKILL / "scripts" / "build_primer.py"),
            str(SKILL / "templates" / "example-primer.json"),
            "--output",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    built = json.loads(build.stdout)
    package = Path(built["package"])
    assert built["recommendedSurface"] == "ipad"
    assert built["containsSecrets"] is False

    verify = subprocess.run(  # noqa: S603 - fixed interpreter and repository script
        [sys.executable, str(SKILL / "scripts" / "verify_package.py"), str(package)],
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(verify.stdout)
    assert result == {
        "valid": True,
        "containsSecrets": False,
        "projectSlug": "example-site",
        "previewVersion": None,
        "previewPages": 0,
        "members": ["manifest.json", "primer.json", "project.json"],
    }


def test_agent_preview_builds_ordered_rendered_version(tmp_path: Path) -> None:
    renders = tmp_path / "renders"
    renders.mkdir()
    # Valid 1x1 sRGB PNG. The builder validates the PNG signature, IHDR,
    # pixel budget, path containment, and ZIP integrity independently.
    png = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    )
    (renders / "home.png").write_bytes(png)
    (renders / "pricing.png").write_bytes(png)
    preview = {
        "label": "Hermes Preview",
        "captured_at": "2026-07-16T20:00:00Z",
        "captured_with": "chromium",
        "viewport": "desktop",
        "color_scheme": "light",
        "pages": [
            {
                "url": "https://example.com/",
                "page_slug": "home",
                "page_title": "Home",
                "screenshot": "renders/home.png",
                "viewport_width": 1440,
                "viewport_height": 900,
                "scroll_height": 2400,
            },
            {
                "url": "https://example.com/pricing",
                "page_slug": "pricing",
                "page_title": "Pricing",
                "screenshot": "renders/pricing.png",
                "viewport_width": 1440,
                "viewport_height": 900,
                "scroll_height": 1800,
            },
        ],
    }
    preview_path = tmp_path / "preview.json"
    preview_path.write_text(json.dumps(preview), encoding="utf-8")

    build = subprocess.run(  # noqa: S603 - fixed interpreter and repository script
        [
            sys.executable,
            str(SKILL / "scripts" / "build_primer.py"),
            str(SKILL / "templates" / "example-primer.json"),
            "--preview",
            str(preview_path),
            "--output",
            str(tmp_path / "out"),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    built = json.loads(build.stdout)
    package = Path(built["package"])
    assert built["previewPages"] == 2

    verify = subprocess.run(  # noqa: S603 - fixed interpreter and repository script
        [sys.executable, str(SKILL / "scripts" / "verify_package.py"), str(package)],
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(verify.stdout)
    assert result["previewVersion"] == "Hermes Preview"
    assert result["previewPages"] == 2
    assert result["containsSecrets"] is False

    telegram_package = tmp_path / "HermesTest.monetproj.zip"
    telegram_package.write_bytes(package.read_bytes())
    telegram_verify = subprocess.run(  # noqa: S603 - fixed interpreter and repository script
        [sys.executable, str(SKILL / "scripts" / "verify_package.py"), str(telegram_package)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(telegram_verify.stdout)["previewPages"] == 2

    with zipfile.ZipFile(package) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        version = json.loads(archive.read("versions/hermes-preview/version.json"))
    assert manifest["versionCount"] == 1
    assert version["captureKind"] == "agent-preview"
    assert [page["pageSlug"] for page in version["pages"]] == ["home", "pricing"]
    assert [page["reviewOrder"] for page in version["pages"]] == [0, 1]

    unsafe_package = tmp_path / "unsafe-scheme.monetproj"
    with zipfile.ZipFile(package) as source, zipfile.ZipFile(
        unsafe_package, "w", compression=zipfile.ZIP_DEFLATED
    ) as destination:
        for member in source.infolist():
            body = source.read(member.filename)
            if member.filename == "versions/hermes-preview/version.json":
                tampered = json.loads(body)
                tampered["pages"][0]["url"] = "ftp://example.com/"
                body = json.dumps(tampered).encode("utf-8")
            destination.writestr(member.filename, body)
    unsafe_verify = subprocess.run(  # noqa: S603 - fixed interpreter and repository script
        [sys.executable, str(SKILL / "scripts" / "verify_package.py"), str(unsafe_package)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert unsafe_verify.returncode == 2
    assert "does not match the configured project" in unsafe_verify.stderr


def test_runtime_rejects_values_the_ipad_wire_cannot_accept() -> None:
    def example() -> dict[str, Any]:
        return json.loads((SKILL / "templates" / "example-primer.json").read_text(encoding="utf-8"))

    unsafe_payloads: list[dict[str, Any]] = []

    traversal = example()
    traversal["project"]["repository"]["design_paths"] = ["../.env"]
    unsafe_payloads.append(traversal)

    duplicate_resource = example()
    resources = duplicate_resource["connectors"][0]["resources"]
    resources.append(dict(resources[0]))
    unsafe_payloads.append(duplicate_resource)

    oversized_design = example()
    oversized_design["project"]["design_markdown"] = "x" * 200_001
    unsafe_payloads.append(oversized_design)

    credential_query = example()
    credential_query["project"]["dev_url"] = "https://example.com?authorization=value"
    unsafe_payloads.append(credential_query)

    oversized_stack_item = example()
    oversized_stack_item["stack"]["frameworks"] = ["x" * 121]
    unsafe_payloads.append(oversized_stack_item)

    for payload in unsafe_payloads:
        with pytest.raises(PrimerError):
            load_project_primer(payload)


def test_cli_validation_failure_never_echoes_submitted_secret(tmp_path: Path) -> None:
    payload = json.loads(
        (SKILL / "templates" / "example-primer.json").read_text(encoding="utf-8")
    )
    submitted_secret = "ghp_abcdefghijklmnopqrstuvwxyz0123456789"
    payload["connectors"][0]["kind"] = submitted_secret
    primer_path = tmp_path / "unsafe-primer.json"
    primer_path.write_text(json.dumps(payload), encoding="utf-8")

    result = subprocess.run(  # noqa: S603 - fixed interpreter and repository script
        [
            sys.executable,
            str(SKILL / "scripts" / "build_primer.py"),
            str(primer_path),
            "--output",
            str(tmp_path / "out"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert submitted_secret not in result.stdout
    assert submitted_secret not in result.stderr
    assert "connectors.0.kind" in result.stderr
    assert "unsupported connector kind" in result.stderr

"""Publication smoke tests for the Monet Hermes community tap."""

from __future__ import annotations

import json
import re
import subprocess
import sys
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
        "members": ["manifest.json", "primer.json", "project.json"],
    }


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

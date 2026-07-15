#!/usr/bin/env python3
"""Verify a configuration-only Project Primer package before handoff."""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path, PurePosixPath

MAX_PACKAGE_BYTES = 5 * 1024 * 1024
MAX_MEMBER_BYTES = 512 * 1024
EXPECTED_MEMBERS = {"manifest.json", "project.json", "primer.json"}


def _load_validator():
    try:
        from monet.project_primer import load_project_primer  # type: ignore[import-not-found]
    except ImportError:
        from project_primer_runtime import load_project_primer  # type: ignore[import-not-found]
    return load_project_primer


def verify(path: Path) -> dict[str, object]:
    if path.suffix.lower() != ".monetproj" or not path.is_file():
        raise ValueError("Expected an existing .monetproj file.")
    if path.stat().st_size > MAX_PACKAGE_BYTES:
        raise ValueError("Primer package exceeds the safe size limit.")

    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)) or set(names) != EXPECTED_MEMBERS:
            raise ValueError("Primer package must contain exactly three expected members.")
        for info in infos:
            member = PurePosixPath(info.filename)
            if member.is_absolute() or ".." in member.parts or info.file_size > MAX_MEMBER_BYTES:
                raise ValueError("Primer package contains an unsafe member.")
            if info.flag_bits & 0x1:
                raise ValueError("Primer package members must not use ZIP encryption.")

        manifest = json.loads(archive.read("manifest.json"))
        project = json.loads(archive.read("project.json"))
        primer = _load_validator()(archive.read("primer.json"))

    if manifest.get("formatVersion") != 1 or manifest.get("versionCount") != 0:
        raise ValueError("Primer package manifest is invalid.")
    if project.get("slug") != primer.project.slug:
        raise ValueError("Project and Primer slugs do not match.")
    return {
        "valid": True,
        "containsSecrets": False,
        "projectSlug": primer.project.slug,
        "members": sorted(EXPECTED_MEMBERS),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.package), indent=2))
        return 0
    except (OSError, ValueError, zipfile.BadZipFile, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

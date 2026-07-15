#!/usr/bin/env python3
"""Portable Hermes wrapper for Monet's canonical Project Primer builder.

This script intentionally does not implement a second protocol. It locates the
``monet.project_primer`` module provided by Monet Desktop or a source checkout,
then delegates validation and packaging to it. If it is unavailable, the skill
must tell the user to install Monet Desktop or use the Monet MCP integration;
it must not hand-roll an unvalidated package.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load_builder():
    try:
        from monet.project_primer import (  # type: ignore[import-not-found]
            desktop_installation_status,
            encode_setup_url,
            load_project_primer,
            open_package_in_monet,
            write_project_primer_package,
        )

        return (
            desktop_installation_status,
            encode_setup_url,
            load_project_primer,
            open_package_in_monet,
            write_project_primer_package,
        )
    except ImportError:
        from project_primer_runtime import (  # type: ignore[import-not-found]
            desktop_installation_status,
            encode_setup_url,
            load_project_primer,
            open_package_in_monet,
            write_project_primer_package,
        )

        return (
            desktop_installation_status,
            encode_setup_url,
            load_project_primer,
            open_package_in_monet,
            write_project_primer_package,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a validated Monet Project Primer.")
    parser.add_argument("primer", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--open", action="store_true", dest="open_package")
    args = parser.parse_args()

    (
        desktop_installation_status,
        encode_setup_url,
        load_project_primer,
        open_package_in_monet,
        write_project_primer_package,
    ) = _load_builder()
    primer = load_project_primer(args.primer)
    package = write_project_primer_package(primer, args.output)
    result = {
        "package": str(package),
        "setupURL": encode_setup_url(primer),
        "desktop": desktop_installation_status(),
        "recommendedSurface": "ipad",
        "containsSecrets": False,
    }
    print(json.dumps(result, indent=2))
    if args.open_package:
        open_package_in_monet(package)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

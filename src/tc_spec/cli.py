"""
TC Insight – CLI

Interface en ligne de commande du générateur de Specs TC Insight.
"""

import argparse
import logging
import os
import sys
from pathlib import Path

from tc_spec.main import generate_spec
from tc_spec.utils.errors import SpecError

def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tc-spec",
        description="TC Insight Spec Generator (V2)",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    generate = subparsers.add_parser(
        "generate",
        help="Generate a TC Insight spec from an Excel file",
    )

    generate.add_argument(
        "--excel",
        required=True,
        type=Path,
        help="Path to the Excel specification file",
    )

    generate.add_argument(
        "--schema",
        required=True,
        type=Path,
        help="Path to the JSON Schema file",
    )

    generate.add_argument(
        "--out",
        type=Path,
        help="Output JSON file path",
    )

    generate.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate Excel and schema, do not export JSON",
    )

    generate.add_argument(
        "--excel-mode",
        default="machine",
        choices=["machine", "metier"],
        help="Excel format: 'machine' (default) or 'metier' (requires mapping)",
    )

    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()

    log_level = os.getenv("TC_SPEC_LOG_LEVEL", "WARNING").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.WARNING),
        format="%(levelname)s:%(name)s:%(message)s",
    )

    if args.command == "generate":
        if not args.validate_only and not args.out:
            print(
                "Error: --out is required unless --validate-only is set",
                file=sys.stderr,
            )
            sys.exit(2)

        try:
            result = generate_spec(
                excel_path=args.excel,
                output_path=args.out,
                schema_path=args.schema,
                excel_mode=args.excel_mode,
                validate_only=args.validate_only,
            )

            if args.validate_only:
                print("✔ Excel and schema validation successful")
            else:
                print(f"✔ Spec generated successfully: {args.out}")

            sys.exit(0)
        except SpecError as e:
            print(f"✖ Error: {e}", file=sys.stderr)
            sys.exit(1)

        except Exception as e:
            print(
                f"✖ Unexpected error: {e}",
                file=sys.stderr,
            )
            sys.exit(99)
if __name__ == "__main__":
    main()

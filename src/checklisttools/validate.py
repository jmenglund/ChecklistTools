#!/usr/bin/env python3
"""Validate sample metadata before submitting the information to ENA."""

import argparse
import re
import sys
import xml.etree.ElementTree as ET

from importlib.metadata import version
from io import StringIO
from itertools import islice
from typing import Optional

import pandas as pd
import pandera as pa

from .checklistlib import xml_tree_to_checklist
from .helpers import is_file, StoreExpandedPath


__version__ = version("checklisttools")


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    parser = parse_args(args)

    # Parse checklist XML file
    xml_tree = ET.parse(parser.checklist_file)
    checklist = xml_tree_to_checklist(xml_tree)

    # Create validation schemas from checklist
    (units_schema, samples_schema) = checklist.to_pandera_schemas()

    # Read units data
    with open(parser.samples_file) as units_file:
        head = list(islice(units_file, 0, 2))
        head[1] = re.sub("^#units", "", head[1])
        buff = StringIO("".join(head))
        units_frame = pd.read_csv(buff, sep="\t")

    # Read sample data
    samples_frame = pd.read_csv(
        parser.samples_file, sep="\t", skiprows=[1], dtype="str"
    )

    # Validate units and samples
    validate_checklist_schema(units_schema, units_frame)
    samples_failures = validate_checklist_schema(samples_schema, samples_frame)

    if parser.output_file is not None and samples_failures is not None:
        samples_failures.to_csv(parser.output_file, sep="\t")
        print(f'Validation failures saved to file "{parser.output_file}"')


def parse_args(args):
    parser = argparse.ArgumentParser(
        prog="ChecklistTools",
        description=("Validate sample metadata before submitting them to ENA"),
    )
    parser.add_argument(
        "-V", "--version", action="version", version="%(prog)s " + __version__
    )
    parser.add_argument(
        "checklist_file",
        metavar="checklist-file",
        action=StoreExpandedPath,
        type=is_file,
        help="Checkist XML file",
    )
    parser.add_argument(
        "samples_file",
        metavar="samples-file",
        action=StoreExpandedPath,
        type=is_file,
        help="TSV-file with sample metadata",
    )
    parser.add_argument(
        "-o, --output-file",
        dest="output_file",
        metavar="FILE",
        type=str,
        help="output file for storing failure cases (in TSV format)",
    )
    return parser.parse_args(args)


def validate_checklist_schema(
    schema: pa.DataFrameSchema, frame: pd.DataFrame
) -> Optional[pd.DataFrame]:
    try:
        schema.validate(frame, lazy=True)
    except pa.errors.SchemaErrors as err:
        header = compose_error_msg_header(schema)
        msg = reformat_error_msg(str(err), header)
        print(msg)
        return err.failure_cases


def compose_error_msg_header(schema: pa.DataFrameSchema) -> str:
    title = f"VALIDATION ERRORS -- {schema.name.upper()}"
    title_underline = len(title) * "="
    return (
        f"\n{title}\n{title_underline}\n\n"
        f"Checklist: {schema.metadata['checklist_name']} "
        f"({schema.metadata['checklist_id']})"
    )


def reformat_error_msg(msg: str, header: str) -> str:
    """Trim the pandera error message and add a custom header."""
    msg = re.sub(r"^Schema [\s\S]*: A total of ", "A total of ", msg)
    msg = re.sub(r"\nUsage Tip\n[\s\S]*$", "", msg)
    return f"{header}\n\n{msg}"


if __name__ == "__main__":
    main()

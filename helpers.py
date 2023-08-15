"""Helper functions and classes"""

import argparse
import os
import xml.etree.ElementTree as ET

from dataclasses import asdict, dataclass
from typing import Literal, Optional

import pandera as pa


@dataclass
class ColumnMetadata(object):
    field_group_name: str
    field_group_restriction_type: str
    mandatory: Literal["mandatory", "recommended", "optional"]
    multiplicity: Literal["multiple", "single"]

    dict = asdict


@dataclass
class ColumnRestriction(object):
    dtype: str
    checks: Optional[pa.Check]
    nullable: bool
    required: bool


def is_required(mandatory: Literal["mandatory", "recommended", "optional"]) -> bool:
    required_dict = {
        "mandatory": True,
        "recommended": False,
        "optional": False,
    }
    return required_dict[mandatory]


class StoreExpandedPath(argparse.Action):
    """Invoke shell-like path expansion for user- and relative paths."""

    def __call__(self, parser, namespace, values, option_string=None):
        if values:
            filepath = os.path.abspath(os.path.expanduser(str(values)))
            setattr(namespace, self.dest, filepath)


def is_file(filename):
    """Check if a path is a file."""
    if not os.path.isfile(filename):
        msg = "{0} is not a file".format(filename)
        raise argparse.ArgumentTypeError(msg)
    else:
        return filename


def checklist_to_schemas(
    xml_tree: ET.ElementTree,
) -> tuple[pa.DataFrameSchema, pa.DataFrameSchema]:
    units_columns = {}

    samples_columns = {  # default mandatory columns
        "tax_id": pa.Column("str", pa.Check.str_matches("^\d+$"), required=True),
        "scientific_name": pa.Column("str", required=True),
        "sample_alias": pa.Column("str", required=True, unique=True),
        "sample_title": pa.Column("str", required=True),
        "sample_description": pa.Column("str", required=True),
    }

    root = xml_tree.getroot()
    for field_group in root.findall("./CHECKLIST/DESCRIPTOR/FIELD_GROUP"):
        field_group_name = field_group.find("NAME")
        field_group_restriction_type = field_group.get("restrictionType")
        for field in field_group.findall("./FIELD"):
            col_name = field.find("NAME").text
            col_title = field.find("LABEL").text
            col_description = field.find("DESCRIPTION").text
            col_metadata = ColumnMetadata(
                field_group_name=field_group_name,
                field_group_restriction_type=field_group_restriction_type,
                mandatory=field.find("MANDATORY"),
                multiplicity=field.find("MULTIPLICITY"),
            )
            if field.find("./UNITS"):
                units_restriction = get_units_restriction(field)
                units_column = pa.Column(
                    units_restriction.dtype,
                    checks=units_restriction.checks,
                    name=col_name,
                    required=units_restriction.required,
                    title=col_title,
                    description=col_description,
                    metadata=col_metadata,
                )
                units_columns[units_column.name] = units_column
            samples_restriction = get_samples_restriction(field)
            samples_column = pa.Column(
                samples_restriction.dtype,
                checks=samples_restriction.checks,
                name=col_name,
                required=samples_restriction.required,
                title=col_title,
                description=col_description,
                metadata=col_metadata,
            )
            samples_columns[samples_column.name] = samples_column

    schema_metadata = {
        "checklist_name": root.find("*/DESCRIPTOR/NAME").text,
        "checklist_id": root.find("*/IDENTIFIERS/PRIMARY_ID").text,
    }

    units_schema = pa.DataFrameSchema(
        columns=units_columns, name="units", metadata=schema_metadata
    )
    samples_schema = pa.DataFrameSchema(
        columns=samples_columns, name="samples", metadata=schema_metadata
    )

    return (units_schema, samples_schema)


def get_units_restriction(field: ET.ElementTree) -> ColumnRestriction:
    units = [u.text for u in field.findall("UNITS/UNIT")]
    checks = pa.Check.isin(units)
    required = bool(units) and is_required(field.find("MANDATORY").text)
    return ColumnRestriction(
        dtype="str",
        checks=checks,
        nullable=not required,
        required=required,
    )


def get_samples_restriction(field: ET.ElementTree) -> ColumnRestriction:
    field_type_element = field.find("FIELD_TYPE")
    field_type = field_type_element[0].tag
    if field_type == "TEXT_CHOICE_FIELD":
        text_choice_values = [v.text for v in field_type_element.iter("VALUE")]
        checks = pa.Check.isin(text_choice_values)
    elif field_type == "TEXT_FIELD":
        try:
            regex_value = field_type_element.find("REGEX_VALUE").text
            checks = pa.Check(regex_value=regex_value)
        except AttributeError:
            checks = None
    else:
        raise NotImplementedError

    required = is_required(field.find("MANDATORY").text)

    return ColumnRestriction(
        dtype="str",
        checks=checks,
        nullable=not required,
        required=required,
    )

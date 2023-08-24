import xml.etree.ElementTree as ET

from dataclasses import dataclass
from typing import Literal, Optional

import pandera as pa


@dataclass(kw_only=True)
class Field(object):
    name: str
    label: str
    description: str
    synonyms: list[str]
    mandatory: Literal["mandatory", "recommended", "optional"]
    multiplicity: str
    units: list[str]

    @property
    def _pandera_required(self) -> bool:
        required_dict = {
            "mandatory": True,
            "recommended": False,
            "optional": False,
        }
        return required_dict[self.mandatory]

    @staticmethod
    def get_field_by_type(field_type, **kwargs):
        if field_type == "TEXT_FIELD":
            return TextField(**kwargs)
        elif field_type == "TEXT_CHOICE_FIELD":
            return TextChoiceField(**kwargs)
        else:
            print(f"Unknown field type: {field_type}")
            raise NotImplementedError

    @property
    def pandera_samples_column(self):
        return pa.Column(
            "str",
            name=self.name,
            checks=self._pandera_samples_check,
            title=self.label,
            description=self.description,
            nullable=not self._pandera_required,
            required=self._pandera_required,
        )

    @property
    def pandera_units_column(self):
        if bool(self.units):
            checks = pa.Check.isin(self.units)
        else:
            checks = None
        required = self._pandera_required and bool(self.units)

        return pa.Column(
            "str",
            name=self.name,
            checks=checks,
            title=self.label,
            description=self.description,
            nullable=not required,
            required=required,
        )


@dataclass(kw_only=True)
class TextField(Field):
    regex_value: Optional[str]

    @property
    def _pandera_samples_check(self):
        if self.regex_value is not None:
            self.checks = pa.Check.str_matches(self.regex_value)
        else:
            self.checks = None


@dataclass(kw_only=True)
class TextChoiceField(Field):
    text_choice_values: list[str]

    @property
    def _pandera_samples_check(self):
        return pa.Check.isin(self.text_choice_values)


@dataclass
class FieldGroup(object):
    name: str
    restriction: str
    fields: list[Field]


@dataclass
class Checklist(object):
    accession: str
    checklist_type: str
    primary_id: str
    label: str
    name: str
    description: str
    authority: str
    field_groups: list[FieldGroup]

    def to_pandera_schemas(self) -> tuple[pa.DataFrameSchema, pa.DataFrameSchema]:
        units_columns = {}
        samples_columns = {  # default mandatory columns
            "tax_id": pa.Column("str", pa.Check.str_matches("^\d+$"), required=True),
            "scientific_name": pa.Column("str", required=True),
            "sample_alias": pa.Column("str", required=True, unique=True),
            "sample_title": pa.Column("str", required=True),
            "sample_description": pa.Column("str", required=True),
        }
        for field_group in self.field_groups:
            for field in field_group.fields:
                if bool(field.units):
                    units_columns[field.name] = field.pandera_units_column
                samples_columns[field.name] = field.pandera_samples_column

        schema_metadata = {
            "checklist_name": self.name,
            "checklist_id": self.primary_id,
        }
        units_schema = pa.DataFrameSchema(
            units_columns,
            name="units",
            metadata=schema_metadata,
        )
        samples_schema = pa.DataFrameSchema(
            samples_columns,
            name="samples",
            metadata=schema_metadata,
        )
        return (units_schema, samples_schema)


def xml_tree_to_checklist(xml_tree: ET.ElementTree) -> Checklist:
    root = xml_tree.getroot()
    field_groups = []
    for fg_element in root.findall("./CHECKLIST/DESCRIPTOR/FIELD_GROUP"):
        fields = []
        for field_element in fg_element.findall("./FIELD"):
            field_type_element = field_element.find("FIELD_TYPE")
            field_type = field_type_element[0].tag

            units = [u.text for u in field_element.findall("UNITS/UNIT")]

            field_kwargs = {
                "name": field_element.find("NAME").text,
                "label": field_element.find("LABEL").text,
                "description": field_element.find("DESCRIPTION").text,
                "synonyms": [s.text for s in field_element.findall("SYNONYM")],
                "mandatory": field_element.find("MANDATORY").text,
                "multiplicity": field_element.find("MULTIPLICITY").text,
                "units": units,
            }
            if field_type == "TEXT_CHOICE_FIELD":
                field_kwargs["text_choice_values"] = [
                    v.text for v in field_type_element.iter("VALUE")
                ]
            elif field_type == "TEXT_FIELD":
                try:
                    regex_value = field_type_element.find("TEXT_FIELD/REGEX_VALUE").text
                    field_kwargs["regex_value"] = regex_value
                except AttributeError:
                    field_kwargs["regex_value"] = None
            else:
                pass
            field = Field.get_field_by_type(field_type, **field_kwargs)
            fields.append(field)
        field_group = FieldGroup(
            name=fg_element.find("NAME").text,
            restriction=fg_element.get("restrictionType"),
            fields=fields,
        )
        field_groups.append(field_group)

    checklist = Checklist(
        accession=root.find("CHECKLIST").get("accession"),
        checklist_type=root.find("CHECKLIST").get("checklistType"),
        primary_id=root.find("CHECKLIST/IDENTIFIERS/PRIMARY_ID").text,
        label=root.find("CHECKLIST/DESCRIPTOR/LABEL").text,
        name=root.find("CHECKLIST/DESCRIPTOR/NAME").text,
        description=root.find("CHECKLIST/DESCRIPTOR/DESCRIPTION").text,
        authority=root.find("CHECKLIST/DESCRIPTOR/AUTHORITY").text,
        field_groups=field_groups,
    )
    return checklist

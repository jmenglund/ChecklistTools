#!/usr/bin/env python3
"""
Create template for entering sample metadata based on an ENA checklist.


1. Read specification of checklist in XML format
2. Create an Excel workbook
3. Create an Excel worksheet
4. Write data to columns:
    * column header
    * column description (as comment)
    * add dropdown list if options are available
    * add conditional formatting (if relevant)
    * indicate mandatory fields
5. Save Excel-file

-----

# v0.1 (MVP)

* Input: parse checklist XML-file
* Output: Excel-file with column headers and column descriptions
* Hardcoded input and output filenames


# v0.2

* Dropdown lists for valid options



# v0.3

* Input format: text, number, date etc.
* Filenames provided via the command-line:
    generate_template input-file output-file


# v0.4

* Conditional formatting according to restrictions in single cells


# v0.5

* Indicate field groups
* Restrictions based on field groups

*****************

define style for invalid
define style for invalid and recommended

for each column:
    write header with column name to sheet "Samples", "Value lists" and "Validation"
    (add unit(s))
    if value list:
        write value list to sheet "Value lists"
        get value list range
        define name for value list range
        write validation formulas to sheet "Validation": =NOT(ISNA(MATCH(T7,W$2:W$288,0)=1))
    if regex:
        write validation formulas to sheet "Validation"
    add conditional formatting

"""
from typing import Optional

import pandas as pd
import pandera as pa
import xlsxwriter
import xml.etree.ElementTree as ET

from xlsxwriter.utility import xl_range_abs

from .checklistlib import xml_tree_to_checklist, Field


def add_checklist_field(field: Field):
    # Add value list (if there is one) with header to sheet
    # Add unit value list with header
    # Create validation formula function
    # Add validation formulas to validation sheet
    # Add column header to samples
    # Add unit dropdown (if relevant)
    # Add conditional formatting
    # Add dropdown list (if relevant)
    pass


def add_value_list_column(field_name, field_id, value_list=None):
    pass

def add_validation_column(field_name, field_id, num_rows, formula_func):
    pass


def get_regex_formula(field_name, field_id, row_id):
    pass


def get_value_list_formula(field_name, field_id, row_id):
    pass

def add_samples_column(field_name, field_id):
    pass


def main():
    # Create workbook
    workbook = xlsxwriter.Workbook("/Users/markus/Desktop/checklist_tmp/template.xlsx")
    readme_sheet = workbook.add_worksheet("README")
    samples_sheet = workbook.add_worksheet("Samples")
    restrictions_sheet = workbook.add_worksheet("Restrictions")
    validation_sheet = workbook.add_worksheet("Validation")

    # Parse checklist XML file
    xml_tree = ET.parse("/Users/markus/Desktop/checklist_tmp/example_checklists/ERC000030.xml")
    # Create validation schemas from checklist
    checklist = xml_tree_to_checklist(xml_tree)

    col_id = 0
    for field_group in checklist.field_groups:
        for field in field_group.fields:
            restrictions_sheet.write(0, col_id, field.name)  # header
            try:
                # Write value list
                allowed_values = field.text_choice_values
                for (row, val) in enumerate(allowed_values, 1):
                    restrictions_sheet.write(row, col_id, val)
                # Write validation formulas
            except AttributeError:
                try:
                    # Write regex
                    regex_value = field.regex_value
                    restrictions_sheet.write(1, col_id, regex_value)
                    # Write validation formulas
                except AttributeError:
                    pass
            # Write sample sheet column
            # Add conditional formatting
            col_id += 1



    # for col_name, col in samples_schema.columns.items():
    #     # Write headers
    #     samples_sheet.write(0, col_id, col_name)
    #     value_lists_sheet.write(0, col_id, col_name)
    #     validation_sheet.write(0, col_id, col_name)

    #     print(col_name)

    #     if bool(col.checks):
    #         # Write value list if one exists
    #         try:
    #             allowed_values = sorted(col.checks[0]._check_kwargs["allowed_values"])
    #             for (row, val) in enumerate(allowed_values, 1):
    #                 value_lists_sheet.write(row, col_id, val)
    #             vl_range = xl_range_abs(1, col_id, row, col_id)
    #             workbook.define_name(f"value_list_{col_id}", f"=Value lists!{vl_range}")
    #             print("  value list")
    #         except KeyError as e1:
    #             try:
    #                 regex = col.checks[0]._check_kwargs["pattern"]
    #                 print("  ", regex)
    #             except KeyError as e2:
    #                 print("  other")

    #     col_id += 1  # next column

    workbook.close()

if __name__ == "__main__":
    main()

# helpers/flatten_xml.py

import xml.etree.ElementTree as ET
from pyspark.sql import Row
import logging


def flatten_xml_element(elem, parent_key='', sep='_'):
    """
    Flatten XML recursively.
    """
    items = {}
    for child in elem:
        new_key = parent_key + sep + child.tag if parent_key else child.tag
        items.update(flatten_xml_element(child, new_key, sep=sep))
    items[parent_key] = elem.text
    return items


def flatten_xml_column(xml_content: str) -> Row:
    """
    Convert XML string to a flattened Row object.
    """
    try:
        root = ET.fromstring(xml_content)
        flattened_data = flatten_xml_element(root)
        row = Row(**flattened_data)
        return row

    except Exception as e:
        logging.error(f"Error flattening XML: {e}")
        raise e


def flatten_xml(df, column_name):
    """
    Function to flatten XML data from the specified column.
    """
    try:
        flattened_rdd = df.rdd.map(lambda row: flatten_xml_column(row[column_name]))
        flattened_df = df.spark.createDataFrame(flattened_rdd)

        logging.info("XML flattening successful for the given column.")
        return flattened_df

    except Exception as e:
        logging.error(f"Error in flattening dataframe with XML column: {e}")
        raise e

# helpers/parse_xml.py
import logging
import xml.etree.ElementTree as ET


def parse_xml(content: str):
    """
    Function to parse XML from the given content.
    """
    try:
        # Parse the XML string
        tree = ET.ElementTree(ET.fromstring(content))
        root = tree.getroot()

        # You can return the entire XML as a string (or any relevant data from the parsed XML)
        return ET.tostring(root, encoding='utf-8').decode('utf-8')

    except Exception as e:
        logging.error(f"Error parsing XML: {e}")
        raise e

import os
import requests
from lxml import etree
import xml.etree.ElementTree as ET   # <-- trūko
import re
import csv

ZUJA_XML = "zuja.xml"
TARGET_XML = "updated_products.xml"
ZUJA_URL = "https://zuja.lt/index.php?route=feed/store/generate&filters=YToyOntzOjI0OiJmaWx0ZXJfY3VzdG9tZXJfZ3JvdXBfaWQiO3M6MjoiMTIiO3M6Mzoia2V5IjtzOjMyOiJjODFlNzI4ZDlkNGMyZjYzNmYwNjdmODljYzE0ODYyYyI7fQ==&key=c81e728d9d4c2f636f067f89cc14862c"  # <- pakeisk į realų URL
# Patikriname, ar zuja.xml egzistuoja ir nėra tuščias
if not os.path.exists("zuja.xml") or os.path.getsize("zuja.xml") == 0:
    raise ValueError("zuja.xml neegzistuoja arba yra tuščias!")

# Parsinamas zuja.xml
zuja_tree = ET.parse("zuja.xml")
zuja_root = zuja_tree.getroot()

# Sukuriame barcode -> total_quantity žemėlapį
zuja_dict = {}
for product in zuja_root.findall(".//product"):
    barcode = product.findtext("barcode")
    quantity = product.findtext("total_quantity")
    if barcode and quantity:
        zuja_dict[barcode] = quantity

# Parsinamas updated_products.xml
if not os.path.exists("updated_products.xml"):
    raise ValueError("updated_products.xml neegzistuoja!")

up_tree = ET.parse("updated_products.xml")
up_root = up_tree.getroot()

# Atitinkamai atnaujiname quantity pagal barcode
for product in up_root.findall(".//product"):
    barcode = product.findtext("barcode")
    if barcode in zuja_dict:
        quantity_elem = product.find("quantity")
        if quantity_elem is not None:
            quantity_elem.text = zuja_dict[barcode]

parser = etree.XMLParser(remove_blank_text=False)
tree_target = etree.parse("updated_products.xml", parser)
root_target = tree_target.getroot()

for el in root_target.xpath("//*[name()='category' or name()='title' or name()='description' or name()='image']"):
    if el.text is not None and not isinstance(el.text, etree.CDATA):
        el.text = etree.CDATA(el.text)

tree_target.write(TARGET_XML, encoding="utf-8", xml_declaration=True, pretty_print=True)
# Išsaugome atnaujintą XML
up_tree.write("updated_products.xml", encoding="utf-8", xml_declaration=True)

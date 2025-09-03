import os
import csv
import requests
import re
from lxml import etree

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

for el in root_target.xpath("//*[name()='category' or name()='title' or name()='description' or name()='image']"):
    if el.text is not None and not isinstance(el.text, etree.CDATA):
        el.text = etree.CDATA(el.text)

tree_target.write(TARGET_XML, encoding="utf-8", xml_declaration=True, pretty_print=True)
# Išsaugome atnaujintą XML
up_tree.write("updated_products.xml", encoding="utf-8", xml_declaration=True)

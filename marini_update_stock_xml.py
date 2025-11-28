import csv
import requests
import re
from lxml import etree

STOCK_CSV = "pakeitimas.csv"
TARGET_XML = "updated_products.xml"


# 4. Redaguojame TARGET_XML tik quantity pagal barcode
with open(TARGET_XML, "r", encoding="utf-8") as f:
    xml_text = f.read()

# Regex, kuris randa <product> bloką su barcode ir quantity
def update_quantity(match):
    product_block = match.group(0)
    barcode_match = re.search(r"<barcode>(.*?)</barcode>", product_block, re.DOTALL)
    if barcode_match:
        barcode = barcode_match.group(1).strip()
        if barcode in stock_dict:
            quantity_new = stock_dict[barcode]
            product_block = re.sub(
                r"(<quantity>).*?(</quantity>)",
                lambda m: f"{m.group(1)}{quantity_new}{m.group(2)}",
                product_block,
                flags=re.DOTALL
            )
    return product_block

xml_text_new = re.sub(r"<product>.*?</product>", update_quantity, xml_text, flags=re.DOTALL)

with open(TARGET_XML, "w", encoding="utf-8") as f:
    f.write(xml_text_new)

print(f"[INFO] {TARGET_XML} atnaujintas pagal stock.csv. CDATA kitur išliko nepakeisti.")

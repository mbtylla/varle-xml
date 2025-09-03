import os
import requests
from lxml import etree
import xml.etree.ElementTree as ET

# -------------------------------
# Konfigūracija
# -------------------------------
ZUJA_XML = "zuja.xml"
TARGET_XML = "updated_products.xml"
ZUJA_URL = "https://zuja.lt/index.php?route=feed/store/generate&filters=YToyOntzOjI0OiJmaWx0ZXJfY3VzdG9tZXJfZ3JvdXBfaWQiO3M6MjoiMTIiO3M6Mzoia2V5IjtzOjMyOiJjODFlNzI4ZDlkNGMyZjYzNmYwNjdmODljYzE0ODYyYyI7fQ==&key=c81e728d9d4c2f636f067f89cc14862c"

# -------------------------------
# 1. Parsisiunčiam zuja.xml
# -------------------------------
def download_zuja():
    print("[INFO] Parsisiunčiam zuja.xml...")
    r = requests.get(ZUJA_URL)
    r.raise_for_status()
    with open(ZUJA_XML, "wb") as f:
        f.write(r.content)
    if os.path.getsize(ZUJA_XML) == 0:
        raise ValueError("zuja.xml parsisiųstas, bet failas tuščias!")

if not os.path.exists(ZUJA_XML) or os.path.getsize(ZUJA_XML) == 0:
    download_zuja()

# -------------------------------
# 2. Perskaityti zuja.xml
# -------------------------------
zuja_tree = ET.parse(ZUJA_XML)
zuja_root = zuja_tree.getroot()

stock_map = {}
for item in zuja_root.findall(".//item"):
    brc = item.findtext("barcode")
    qty = item.findtext("total_quantity")
    if brc and qty:
        brc_clean = brc.strip().lstrip("0")  # normalizuojam barcode
        stock_map[brc_clean] = qty.strip()

print(f"[INFO] Prekių zuja.xml: {len(stock_map)}")

# -------------------------------
# 3. Perskaityti target XML
# -------------------------------
parser = etree.XMLParser(remove_blank_text=False)
tree_target = etree.parse(TARGET_XML, parser)
root_target = tree_target.getroot()

# -------------------------------
# 4. Atnaujinti quantity pagal barcode
# -------------------------------
count_updated = 0
for product in root_target.findall(".//product"):
    barcode_el = product.find("barcode")
    qty_el = product.find("quantity")
    if barcode_el is not None and qty_el is not None:
        barcode_clean = barcode_el.text.strip().lstrip("0")
        if barcode_clean in stock_map:
            old_qty = qty_el.text
            qty_el.text = stock_map[barcode_clean]
            count_updated += 1
            print(f"[DEBUG] {barcode_clean}: {old_qty} -> {qty_el.text}")

print(f"[INFO] Atnaujinta prekių: {count_updated}")

# -------------------------------
# 5. Išlaikyti CDATA tam tikriems laukams
# -------------------------------
for el in root_target.xpath("//*[name()='category' or name()='title' or name()='description' or name()='image']"):
    if el.text:
        el.text = etree.CDATA(el.text)

# -------------------------------
# 6. Išsaugoti XML
# -------------------------------
tree_target.write(
    TARGET_XML,
    pretty_print=True,
    encoding="utf-8",
    xml_declaration=True
)

print("[INFO] updated_products.xml atnaujintas sėkmingai.")

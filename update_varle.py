import os
import requests
import xml.etree.ElementTree as ET
from lxml import etree
import csv

ZUJA_XML = "zuja.xml"
TARGET_XML = "updated_products.xml"
ZUJA_URL = "https://zuja.lt/index.php?route=feed/store/generate&filters=YToyOntzOjI0OiJmaWx0ZXJfY3VzdG9tZXJfZ3JvdXBfaWQiO3M6MjoiMTIiO3M6Mzoia2V5IjtzOjMyOiJjODFlNzI4ZDlkNGMyZjYzNmYwNjdmODljYzE0ODYyYyI7fQ==&key=c81e728d9d4c2f636f067f89cc14862c"  # <-- tikras URL

# -------------------------------
# 1. Parsisiunčiam zuja.xml, jei jo nėra arba failas tuščias
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
# 2. Skaitom zuja.xml su ElementTree
# -------------------------------
zuja_tree = ET.parse(ZUJA_XML)
zuja_root = zuja_tree.getroot()

# -------------------------------
# 3. Sudarom barcode -> quantity žemėlapį
# -------------------------------
stock_map = {}
for item in zuja_root.findall(".//item"):
    brc = item.findtext("barcode")
    qty = item.findtext("total_quantity")
    if brc and qty:
        brc = brc.strip().lstrip("0")  # pašalinam pradinius nulius
        stock_map[brc] = qty.strip()

print(f"[INFO] Iš viso prekių zuja.xml: {len(stock_map)}")

# -------------------------------
# 4. Skaitom target XML su lxml, kad galėtume tvarkyti CDATA
# -------------------------------
parser = etree.XMLParser(remove_blank_text=False)
tree_target = etree.parse(TARGET_XML, parser)
root_target = tree_target.getroot()

# -------------------------------
# 5. Atnaujinam quantity pagal barcode
# -------------------------------
count_updated = 0
for product in root_target.findall(".//product"):
    barcode_el = product.find("barcode")
    qty_el = product.find("quantity")
    if barcode_el is not None and qty_el is not None:
        barcode_clean = barcode_el.text.strip().lstrip("0")
        if barcode_clean in stock_map:
            qty_el.text = stock_map[barcode_clean]
            count_updated += 1
            print(f"[DEBUG] Updated {barcode_clean} -> {qty_el.text}")

print(f"[INFO] Atnaujinta prekių: {count_updated}")

# -------------------------------
# 6. CDATA grąžinam tik reikiamiems laukams
# -------------------------------
for el in root_target.xpath("//*[name()='category' or name()='title' or name()='description' or name()='image']"):
    if el.text:
        el.text = etree.CDATA(el.text)

# -------------------------------
# 7. Išsaugom target XML
# -------------------------------
tree_target.write(
    TARGET_XML,
    pretty_print=True,
    encoding="utf-8",
    xml_declaration=True
)

print("[INFO] updated_products.xml atnaujintas sėkmingai.")

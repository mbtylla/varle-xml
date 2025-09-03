import xml.etree.ElementTree as ET
import csv
import os
import requests
import shutil

INPUT_XML = "marini-b2b.xml"
STOCK_CSV = "stock.csv"
TARGET_XML = "marinitestas.xml"
URL = "https://marini.pl/b2b/marini-b2b.xml"

STOCK_MAP = {
    "brak": 0,
    "mała ilość": 2,
    "średnia ilość": 5,
    "duża ilość": 15
}

def normalize_stock(value):
    if value is None:
        return 0
    value = value.strip().lower()
    return str(STOCK_MAP.get(value, value))

# 1. Parsisiunčiame XML
r = requests.get(URL)
r.raise_for_status()
with open(INPUT_XML, "wb") as f:
    f.write(r.content)
print(f"[INFO] {INPUT_XML} parsisiųstas.")

# 2. Generuojame stock.csv
tree = ET.parse(INPUT_XML)
root = tree.getroot()

with open(STOCK_CSV, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["EAN", "stan"])
    for b2b in root.findall(".//b2b"):  # pakeista į b2b
        ean = b2b.findtext("EAN")
        stan = b2b.findtext("stan")
        if ean and stan:
            normalized = normalize_stock(stan)
            writer.writerow([ean.strip(), normalized])
print(f"[INFO] {STOCK_CSV} sugeneruotas.")

# 3. Atnaujiname TARGET_XML pagal stock.csv
if not os.path.exists(TARGET_XML):
    print(f"[WARN] {TARGET_XML} neegzistuoja, sukuriamas naujas failas.")
    shutil.copy(INPUT_XML, TARGET_XML)

# Įkeliame stock.csv į dict
stock_dict = {}
with open(STOCK_CSV, newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        stock_dict[row["EAN"].strip()] = row["stan"].strip()

# Redaguojame Marinitestas.xml
tree_target = ET.parse(TARGET_XML)
root_target = tree_target.getroot()
updated_count = 0

for product in root_target.findall(".//product"):
    barcode = product.findtext("barcode")
    if barcode:
        barcode_clean = barcode.strip()
        if barcode_clean in stock_dict:
            quantity_el = product.find("quantity")
            if quantity_el is not None:
                old_value = quantity_el.text
                quantity_el.text = stock_dict[barcode_clean]
                updated_count += 1
                print(f"[UPDATE] Barcode {barcode_clean}: {old_value} -> {quantity_el.text}")

tree_target.write(TARGET_XML, encoding="utf-8", xml_declaration=True)
print(f"[INFO] {TARGET_XML} atnaujintas. Pakeista {updated_count} prekių likučiai.")

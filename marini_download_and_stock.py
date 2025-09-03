import requests
import xml.etree.ElementTree as ET
import csv

INPUT_FILE = "marini-b2b.xml"
OUTPUT_FILE = "stock.csv"
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
    return STOCK_MAP.get(value, value)

# Parsisiunčia XML
print("[INFO] Parsisiunčiamas XML...")
r = requests.get(URL)
r.raise_for_status()
with open(INPUT_FILE, "wb") as f:
    f.write(r.content)
print(f"[INFO] Failas {INPUT_FILE} sėkmingai parsisiųstas.")

# Generuoja stock.csv
tree = ET.parse(INPUT_FILE)
root = tree.getroot()

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["EAN", "stan"])

    for product in root.findall(".//produkt"):
        ean = product.findtext("EAN")
        stan = product.findtext("stan")
        if ean and stan:
            normalized = normalize_stock(stan)
            writer.writerow([ean.strip(), normalized])

print(f"[INFO] Duomenys išsaugoti faile {OUTPUT_FILE}")
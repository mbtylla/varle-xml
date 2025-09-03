import csv
import requests
import re

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
b2b_entries = re.findall(r"<b2b>(.*?)</b2b>", r.text, re.DOTALL)
with open(STOCK_CSV, "w", newline="", encoding="utf-8") as csvfile:
    import csv
    writer = csv.writer(csvfile)
    writer.writerow(["EAN", "stan"])
    for entry in b2b_entries:
        ean_match = re.search(r"<EAN>(.*?)</EAN>", entry, re.DOTALL)
        stan_match = re.search(r"<stan>(.*?)</stan>", entry, re.DOTALL)
        if ean_match and stan_match:
            ean = ean_match.group(1).strip()
            stan = normalize_stock(stan_match.group(1))
            writer.writerow([ean, stan])
print(f"[INFO] {STOCK_CSV} sugeneruotas.")

# 3. Įkeliame stock.csv į dict
stock_dict = {}
with open(STOCK_CSV, newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        stock_dict[row["EAN"].strip()] = row["stan"].strip()

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
            # Pakeičiam <quantity>...</quantity> bet išlaikom kitus tag'us su CDATA
            product_block = re.sub(
                r"(<quantity>).*?(</quantity>)",
                r"\1{}\2".format(quantity_new),
                product_block,
                flags=re.DOTALL
            )
    return product_block

xml_text_new = re.sub(r"<product>.*?</product>", update_quantity, xml_text, flags=re.DOTALL)

with open(TARGET_XML, "w", encoding="utf-8") as f:
    f.write(xml_text_new)

print(f"[INFO] {TARGET_XML} atnaujintas pagal stock.csv. CDATA kitur išliko nepakeisti.")

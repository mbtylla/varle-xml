import requests
import re
from lxml import etree

# ---- FAILAI ----
INPUT_XML = "anvol.xml"              # čia saugosime parsisiųstą ANVOL XML
TARGET_XML = "updated_products.xml"  # failas, kurį atnaujinsime

# ---- ANVOL XML NUORODA ----
ANVOL_URL = "https://xml.anvol.eu/wholesale-lt-products.xml"


# -----------------------------------------------------------
# 1. Parsisiunčiame ANVOL XML
# -----------------------------------------------------------
r = requests.get(ANVOL_URL)
r.raise_for_status()

with open(INPUT_XML, "wb") as f:
    f.write(r.content)

print("[INFO] ANVOL XML atsisiųstas.")


# -----------------------------------------------------------
# 2. Nuskaitome ANVOL XML → sudarome {ean: stock_ee}
# -----------------------------------------------------------
tree = etree.fromstring(r.content)
products = tree.findall(".//product")

anvol_stock = {}

for p in products:
    ean = p.findtext("ean")
    stock_ee = p.findtext("stocks/stock_ee")

    if ean:
        clean_ean = ean.strip()
        quantity = stock_ee.strip() if stock_ee else "0"
        anvol_stock[clean_ean] = quantity

print(f"[INFO] Rasta ANVOL prekių: {len(anvol_stock)}")


# -----------------------------------------------------------
# 3. Atidarome tavo XML ir perrašome <quantity> pagal EAN
# -----------------------------------------------------------
with open(TARGET_XML, "r", encoding="utf-8") as f:
    xml_text = f.read()

stock_dict = {}   # ← Bendras žodynas

with open(ANVOL_STOCK_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        stock_dict[row["ean"].strip()] = row["stock_ee"].strip()

def update_quantity(match):
    block = match.group(0)  # ← čia buvo klaida: reikia tekstą, ne match objektą

    barcode_match = re.search(r"<barcode>(.*?)</barcode>", block, re.DOTALL)
    if barcode_match:
        barcode = barcode_match.group(1).strip()

        if barcode in stock_dict:
            new_qty = stock_dict[barcode]

            block = re.sub(
                r"(<quantity>).*?(</quantity>)",
                lambda m: f"{m.group(1)}{new_qty}{m.group(2)}",
                block,
                flags=re.DOTALL
            )

    return block


updated_xml = re.sub(r"<product>.*?</product>", update_quantity, xml_text, flags=re.DOTALL)


with open(TARGET_XML, "w", encoding="utf-8") as f:
    f.write(updated_xml)

print("[INFO] TARGET_XML sėkmingai atnaujintas pagal ANVOL likučius!")

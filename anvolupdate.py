import requests
from lxml import etree
import re
import csv

# 1. Parsisiunčiam ANVOL XML
URL = "https://xml.anvol.eu/wholesale-lt-products.xml"
r = requests.get(URL)
r.raise_for_status()
tree = etree.fromstring(r.content)
print(f"[INFO] ANVOL XML atsisiųstas.")
products = tree.findall(".//product")
print(f"[INFO] Rasta ANVOL prekių: {len(products)}")

# 2. Sudarome stock_dict pagal <ean> -> <stock_ee>
stock_dict = {}
ANVOL_STOCK_CSV = "anvolstocks.csv"

with open(ANVOL_STOCK_CSV, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["ean", "stock_ee"])  # antraštės
    for product in products:
        ean = product.findtext("ean")
        stock_ee = product.findtext("stocks/stock_ee")
        if ean:
            qty = stock_ee.strip() if stock_ee else "0"
            stock_dict[ean.strip()] = qty
            writer.writerow([ean.strip(), qty])

print(f"[INFO] {ANVOL_STOCK_CSV} sugeneruotas.")

# 3. Atidarom target XML
TARGET_XML = "updated_products.xml"
with open(TARGET_XML, "r", encoding="utf-8") as f:
    xml_text = f.read()

# 4. Funkcija, kuri atnaujina quantity pagal EAN
def update_quantity(match):
    block = match.group(0)
    barcode_match = re.search(r"<barcode>(.*?)</barcode>", block, re.DOTALL)
    if not barcode_match:
        return block
    barcode = barcode_match.group(1).strip()
    if barcode in stock_dict:
        qty = stock_dict[barcode]
        block = re.sub(
            r"(<quantity>).*?(</quantity>)",
            lambda m: f"{m.group(1)}{qty}{m.group(2)}",
            block,
            flags=re.DOTALL
        )
    return block

# 5. Atnaujinam XML
updated_xml = re.sub(r"<product>.*?</product>", update_quantity, xml_text, flags=re.DOTALL)

# 6. Išsaugom atnaujintą XML
with open(TARGET_XML, "w", encoding="utf-8") as f:
    f.write(updated_xml)

print(f"[INFO] {TARGET_XML} atnaujintas pagal ANVOL stock_ee.")

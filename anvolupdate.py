import csv
import requests
import re
from lxml import etree

# ---------- CONFIG ----------
INPUT_XML = "anvol.xml"
STOCKANVOL_CSV = "anvolstocks.csv"
TARGET_XML = "updated_products.xml"
URL = "https://xml.anvol.eu/wholesale-lt-products.xml"

# -------------------------
# 1. Download ANVOL XML
# -------------------------
r = requests.get(URL)
r.raise_for_status()
with open(INPUT_XML, "wb") as f:
    f.write(r.content)
print(f"[INFO] {INPUT_XML} downloaded.")

# -------------------------
# 2. Parse XML and generate stock CSV
# -------------------------
tree = etree.fromstring(r.content)
product_entries = tree.findall(".//product")

with open(STOCKANVOL_CSV, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["ean", "stock_ee"])
    for product in product_entries:
        ean = product.findtext("ean")
        stock_ee = product.findtext("stocks/stock_ee")
        if ean and stock_ee:
            writer.writerow([ean.strip(), stock_ee.strip()])
print(f"[INFO] {STOCKANVOL_CSV} generated.")

# -------------------------
# 3. Load stock CSV into dictionary
# -------------------------
stock_dict = {}
with open(STOCKANVOL_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        stock_dict[row["ean"].strip()] = row["stock_ee"].strip()

# -------------------------
# 4. Read TARGET XML
# -------------------------
with open(TARGET_XML, "r", encoding="utf-8") as f:
    xml_text = f.read()

# -------------------------
# 5. Update quantity in TARGET XML based on barcode
# -------------------------
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

xml_text_new = re.sub(r"<product>.*?</product>", update_quantity, xml_text, flags=re.DOTALL)

# -------------------------
# 6. Save updated XML
# -------------------------
with open(TARGET_XML, "w", encoding="utf-8") as f:
    f.write(xml_text_new)

print(f"[INFO] {TARGET_XML} updated based on {STOCKANVOL_CSV}. CDATA elsewhere remains untouched.")

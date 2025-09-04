import csv
import requests
import re
from lxml import etree

INPUT_XML = "zuja.xml"
STOCKZUJA_CSV = "stockzuja.csv"
TARGET_XML = "updated_products.xml"
URL = "https://zuja.lt/index.php?route=feed/store/generate&filters=YToyOntzOjI0OiJmaWx0ZXJfY3VzdG9tZXJfZ3JvdXBfaWQiO3M6MjoiMTIiO3M6Mzoia2V5IjtzOjMyOiJjODFlNzI4ZDlkNGMyZjYzNmYwNjdmODljYzE0ODYyYyI7fQ==&key=c81e728d9d4c2f636f067f89cc14862c"

# -------------------------
# 1. Download XML
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

with open(STOCKZUJA_CSV, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["barcode", "total_quantity"])
    for product in product_entries:
        barcode = product.findtext("barcode")
        total_quantity = product.findtext("total_quantity")
        if barcode and total_quantity:
            writer.writerow([barcode.strip(), total_quantity.strip()])
print(f"[INFO] {STOCKZUJA_CSV} generated.")

# -------------------------
# 3. Load stock CSV into dictionary
# -------------------------
stockzuja_dict = {}
with open(STOCKZUJA_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        stockzuja_dict[row["barcode"].strip()] = row["total_quantity"].strip()

# -------------------------
# 4. Optional: normalize function
# -------------------------
def normalize_stockzuja(value):
    if value is None:
        return "0"
    value = value.strip().lower()
    return stockzuja_dict.get(value, value)

# -------------------------
# 5. Update TARGET_XML quantities
# -------------------------
with open(TARGET_XML, "r", encoding="utf-8") as f:
    xml_text = f.read()

def update_quantity(match):
    product_block = match.group(0)
    barcode_match = re.search(r"<barcode>(.*?)</barcode>", product_block, re.DOTALL)
    if barcode_match:
        barcode = barcode_match.group(1).strip()
        if barcode in stockzuja_dict:
            quantity_new = stockzuja_dict[barcode]
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

print(f"[INFO] {TARGET_XML} updated based on {STOCKZUJA_CSV}. CDATA elsewhere remains untouched.")

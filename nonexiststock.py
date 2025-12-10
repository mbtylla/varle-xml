import csv
import re

CSV_FILE = "nonexiststock.csv"       # CSV turi stulpelius: EAN, stan
TARGET_XML = "updated_products.xml"

# 1. Nuskaityti CSV į dictionary
stock_dict = {}
with open(CSV_FILE, newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        ean = row.get("EAN", "").strip()
        stan = row.get("stan", "").strip()
        if ean:
            stock_dict[ean] = stan

# 2. Nuskaityti XML tekstą
with open(TARGET_XML, "r", encoding="utf-8") as f:
    xml_text = f.read()

# 3. Funkcija, kuri pakeičia <quantity> tik jei barcode sutampa su CSV
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

# 4. Atnaujinam visus <product> blokus
xml_text_new = re.sub(r"<product>.*?</product>", update_quantity, xml_text, flags=re.DOTALL)

# 5. Išsaugom atnaujintą XML
with open(TARGET_XML, "w", encoding="utf-8") as f:
    f.write(xml_text_new)

print(f"[INFO] {TARGET_XML} atnaujintas pagal {CSV_FILE}. CDATA ir kiti laukai liko nepakitę.")

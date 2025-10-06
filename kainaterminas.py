import csv
import re

STOCK_CSV = "terminaikainos.csv"
TARGET_XML = "testas_products.xml"


with open(STOCK_CSV, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        barcode = row.get("barcode")
        kaina = row.get("price")
        if barcode and price:
            stock_dict[barcode.strip()] = price.strip()

# 4. Redaguojame TARGET_XML tik quantity pagal barcode
with open(TARGET_XML, "r", encoding="utf-8") as f:
    xml_text = f.read()



# Regex, kuris randa <product> bloką su barcode ir quantity
def update_price(match):
    product_block = match.group(0)
    barcode_match = re.search(r"<barcode>(.*?)</barcode>", product_block, re.DOTALL)
    if barcode_match:
        barcode = barcode_match.group(1).strip()
        if barcode in stock_dict:
            price_new = stock_dict[barcode]
            product_block = re.sub(
                r"(<price>).*?(</price>)",
                lambda m: f"{m.group(1)}{price_new}{m.group(2)}",
                product_block,
                flags=re.DOTALL
            )
    return product_block

xml_text_new = re.sub(r"<product>.*?</product>", update_price, xml_text, flags=re.DOTALL)

with open(TARGET_XML, "w", encoding="utf-8") as f:
    f.write(xml_text_new)

print(f"[INFO] {TARGET_XML} atnaujintas pagal stock.csv. CDATA kitur išliko nepakeisti.")

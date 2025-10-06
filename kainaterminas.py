import csv
import re

PRICE_CSV = "terminaikainos.csv"
TARGET_XML = "testas_products.xml"

product_info = {}
with open(PRICE_CSV, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        barcode = row.get("barcode")
        price = row.get("price")
        delivery_text = row.get("delivery_text", "").strip()
        
        if barcode:
            product_info[barcode] = {
                "price": price,
                "delivery_text": delivery_text
            }

# 4. Redaguojame TARGET_XML tik quantity pagal barcode
with open(TARGET_XML, "r", encoding="utf-8") as f:
    xml_text = f.read()



# Regex, kuris randa <product> bloką su barcode ir quantity
def update_product(match):
    product_block = match.group(0)
    barcode_match = re.search(r"<barcode>(.*?)</barcode>", product_block, re.DOTALL)
    if barcode_match:
        barcode = barcode_match.group(1).strip()
        if barcode in product_info:
            info = product_info[barcode]
            price_new = info["price"]
            delivery_text_new = info["delivery_text"]

            # Atnaujinam <price>
            product_block = re.sub(
                r"(<price>).*?(</price>)",
                lambda m: f"{m.group(1)}{price_new}{m.group(2)}",
                product_block,
                flags=re.DOTALL
            )

            # Atnaujinam <delivery_text>
            product_block = re.sub(
                r"(<delivery_text>).*?(</delivery_text>)",
                lambda m: f"{m.group(1)}{delivery_text_new}{m.group(2)}",
                product_block,
                flags=re.DOTALL
            )

    return product_block

xml_text_new = re.sub(r"<product>.*?</product>", update_product, xml_text, flags=re.DOTALL)

with open(TARGET_XML, "w", encoding="utf-8") as f:
    f.write(xml_text_new)

print(f"[INFO] {TARGET_XML} atnaujintas pagal price.csv. CDATA kitur išliko nepakeisti.")

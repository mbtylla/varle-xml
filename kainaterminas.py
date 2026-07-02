import csv
import re

PRICE_CSV = "terminaikainos.csv"
TARGET_XML = "updated_products.xml"

# Nuskaitome CSV
product_info = {}

with open(PRICE_CSV, newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        barcode = row.get("barcode")
        price = row.get("price")
        delivery_text = row.get("delivery_text", "").strip()

        if barcode:
            product_info[barcode.strip()] = {
                "price": price,
                "delivery_text": delivery_text
            }

print("CSV įrašų:", len(product_info))
print("Pirmi 5 barkodai:", list(product_info.keys())[:5])

# Perskaitome XML
with open(TARGET_XML, "r", encoding="utf-8") as f:
    xml_text = f.read()

# Patikriname konkretų barkodą
test = "850036293361"
print("Test barkodas CSV:", test in product_info)
print(
    "Test barkodas XML:",
    re.search(rf"<barcode>\s*{test}\s*</barcode>", xml_text) is not None
)

found = 0

def update_product(match):
    global found

    product_block = match.group(0)

    barcode_match = re.search(
        r"<barcode>(.*?)</barcode>",
        product_block,
        re.DOTALL
    )

    if barcode_match:
        barcode = barcode_match.group(1).strip()

        if barcode in product_info:
            found += 1

            info = product_info[barcode]

            old_price = re.search(
                r"<price>(.*?)</price>",
                product_block,
                re.DOTALL
            ).group(1)

            old_delivery = re.search(
                r"<delivery_text>(.*?)</delivery_text>",
                product_block,
                re.DOTALL
            ).group(1)

            print(
                f"Rastas {barcode}: "
                f"kaina {old_price} -> {info['price']}, "
                f"delivery '{old_delivery}' -> '{info['delivery_text']}'"
            )

            product_block = re.sub(
                r"(<price>).*?(</price>)",
                rf"\g<1>{info['price']}\g<2>",
                product_block,
                flags=re.DOTALL
            )

            product_block = re.sub(
                r"(<delivery_text>).*?(</delivery_text>)",
                rf"\g<1>{info['delivery_text']}\g<2>",
                product_block,
                flags=re.DOTALL
            )

    return product_block


xml_text_new = re.sub(
    r"<product>.*?</product>",
    update_product,
    xml_text,
    flags=re.DOTALL
)

print("Rasta XML produktų:", found)
print("Failas pasikeitė:", xml_text != xml_text_new)

with open(TARGET_XML, "w", encoding="utf-8") as f:
    f.write(xml_text_new)

print(f"[INFO] {TARGET_XML} įrašytas.")

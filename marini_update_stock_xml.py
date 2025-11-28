import csv
import re

CSV_FILE = "pakeitimas.csv"
TARGET_XML = "updated_products.xml"

# 1. Įkeliame pakeitimas.csv → dict {barcode: quantity}
stock_dict = {}

with open(CSV_FILE, newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        barcode = row["EAN"].strip()
        quantity = row["stan"].strip()
        stock_dict[barcode] = quantity

print(f"[INFO] Įkelta barkodų iš CSV: {len(stock_dict)}")

# 2. Perskaitome XML, kurį reikia pataisyti
with open(TARGET_XML, "r", encoding="utf-8") as f:
    xml_text = f.read()


# 3. Funkcija, kuri pakeičia tik quantity, o VISKĄ kitą palieka nepaliestą
def update_quantity(match):
    product_block = match.group(0)

    # randam barcode
    barcode_match = re.search(r"<barcode>(.*?)</barcode>", product_block, re.DOTALL)
    if not barcode_match:
        return product_block  # produktas be barkodo pilnai paliekamas
    
    barcode = barcode_match.group(1).strip()

    # jei barkodas nerastas CSV – neliečiam bloko
    if barcode not in stock_dict:
        return product_block

    new_qty = stock_dict[barcode]

    # pakeičiam tik quantity reikšmę
    product_block = re.sub(
        r"(<quantity>).*?(</quantity>)",
        lambda m: f"{m.group(1)}{new_qty}{m.group(2)}",
        product_block,
        flags=re.DOTALL
    )

    return product_block


# 4. Realiai pritaikome „tekstinį lopymą“
xml_text_new = re.sub(
    r"<product>.*?</product>",
    update_quantity,
    xml_text,
    flags=re.DOTALL
)

# 5. Perrašome failą tuo pačiu pavadinimu
with open(TARGET_XML, "w", encoding="utf-8") as f:
    f.write(xml_text_new)

print(f"[INFO] {TARGET_XML} atnaujintas pagal {CSV_FILE}. Visi kiti laukai (CDATA, formatavimas) palikti nepakeisti.")

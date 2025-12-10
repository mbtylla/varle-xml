import xml.etree.ElementTree as ET
import csv

# 1. NUSKAITOME updated_products.xml
def extract_barcodes_from_updated_products():
    tree = ET.parse("updated_products.xml")
    root = tree.getroot()

    found_barcodes = []

    # iteruojame per visus <product> tagus
    for product in root.findall(".//product"):
        sku = product.findtext("sku", "").strip().lower()

        if sku.startswith("mari"):   # tikrinti ar prasideda "mari"
            barcode = product.findtext("barcode", "").strip()
            if barcode:
                found_barcodes.append(barcode)

    return found_barcodes


# 2. Saugojame egzistuojančius barcodus į egzbarmarini.csv
def save_to_csv(filename, barcodes):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["barcode"])
        for code in barcodes:
            writer.writerow([code])


# 3. Patikriname prieš marini-b2b.xml
def load_b2b_barcodes():
    tree = ET.parse("marini-b2b.xml")
    root = tree.getroot()

    b2b_barcodes = set()

    for product in root.findall(".//product"):
        barcode = product.findtext("barcode", "").strip()
        if barcode:
            b2b_barcodes.add(barcode)

    return b2b_barcodes


def main():
    # 1. Ištraukiame barkodus kurie turi SKU prasidedantį "mari"
    barcodes = extract_barcodes_from_updated_products()
    print(f"Rasta {len(barcodes)} barkodų su SKU prasidedančiu 'mari'.")

    # 2. Išsaugome į egzbarmarini.csv
    save_to_csv("egzbarmarini.csv", barcodes)
    print("Failas egzbarmarini.csv sukurtas.")

    # 3. Užkrauname barkodus iš marini-b2b.xml
    b2b_barcodes = load_b2b_barcodes()

    # 4. Randame barkodus kurių nėra marini-b2b.xml
    not_found = [code for code in barcodes if code not in b2b_barcodes]

    if not_found:
        save_to_csv("NEEGZbarmarini.csv", not_found)
        print(f"Rasta {len(not_found)} neatitikimų. Sukurtas NEEGZbarmarini.csv")
    else:
        print("Visi barkodai egzistuoja marini-b2b.xml faile. NEEGZbarmarini.csv nesukurtas.")


if __name__ == "__main__":
    main()

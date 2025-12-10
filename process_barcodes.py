import xml.etree.ElementTree as ET
import csv
import os


# ---- 1. UPDATED_PRODUCTS.XML ----
def extract_barcodes_from_updated_products():
    tree = ET.parse("updated_products.xml")
    root = tree.getroot()

    found = []

    for product in root.findall(".//product"):
        sku = product.findtext("sku", "").strip().lower()
        if sku.startswith("mari"):
            barcode = product.findtext("barcode", "").strip()
            if barcode:
                found.append(barcode)

    return found


# ---- 2. MARINI-B2B.XML ----
def load_b2b_barcodes():
    tree = ET.parse("marini-b2b.xml")
    root = tree.getroot()

    found = set()

    for item in root.findall(".//b2b"):
        ean = item.findtext("EAN", "").strip()
        if ean:
            found.add(ean)

    return found


# ---- CSV SAVE ----
def save_csv(filename, barcodes):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["barcode"])
        for b in barcodes:
            w.writerow([b])


def main():
    # 1. ištraukiame iš updated_products.xml
    updated = extract_barcodes_from_updated_products()
    print(f"Rasta {len(updated)} barkodų su SKU 'mari*'")

    save_csv("egzbarmarini.csv", updated)
    print("Sukurta: egzbarmarini.csv")

    # 2. užkrauname barkodus iš marini-b2b.xml
    b2b = load_b2b_barcodes()
    print(f"marini-b2b.xml rasta {len(b2b)} barkodų")

    # 3. atfiltruojame kurių nėra
    diff = [b for b in updated if b not in b2b]

    if diff:
        save_csv("NEEGZbarmarini.csv", diff)
        print(f"Sukurta: NEEGZbarmarini.csv ({len(diff)} barkodų)")
    else:
        print("Visi barkodai egzistuoja marini-b2b.xml faile")


if __name__ == "__main__":
    main()

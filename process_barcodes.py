import xml.etree.ElementTree as ET
import csv
import os
import sys


def fail_if_missing(filename):
    if not os.path.exists(filename):
        print(f"ERROR: Nerastas failas: {filename}")
        sys.exit(1)


# ------------------------------------
# 1. UPDATED_PRODUCTS.XML apdorojimas
# ------------------------------------
def extract_from_updated_products():
    fail_if_missing("updated_products.xml")

    tree = ET.parse("updated_products.xml")
    root = tree.getroot()

    found = []

    for product in root.findall(".//product"):

        # pakeista: SKU = <id>
        sku = product.findtext("id", "").strip().lower()

        if not sku:
            continue

        if sku.startswith("mari"):
            barcode = product.findtext("barcode", "").strip()
            if barcode:
                found.append(barcode)

    return found


# ------------------------------------
# 2. MARINI-B2B.XML apdorojimas
# ------------------------------------
def extract_b2b_barcodes():
    fail_if_missing("marini-b2b.xml")

    tree = ET.parse("marini-b2b.xml")
    root = tree.getroot()

    barcodes = set()

    for item in root.findall(".//b2b"):
        ean = item.findtext("EAN", "").strip()
        if ean:
            barcodes.add(ean)

    return barcodes


# ------------------------------------
# CSV išsaugojimas
# ------------------------------------
def save_csv(filename, barcodes):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["barcode"])
        for b in barcodes:
            w.writerow([b])


# ------------------------------------
# MAIN LOGIKA
# ------------------------------------
def main():
    print("Apdorojimas prasidėjo...")

    # 1. updated_products.xml -> barcodai su <id> prasidedančiais 'mari'
    updated = extract_from_updated_products()
    print(f"Rasta SKU 'mari*' produktų: {len(updated)}")

    save_csv("egzbarmarini.csv", updated)
    print("Sukurta: egzbarmarini.csv")

    # 2. marini-b2b.xml -> visi b2b EAN
    b2b = extract_b2b_barcodes()
    print(f"marini-b2b.xml rasta EAN: {len(b2b)}")

    # 3. kurie neradome b2b faile
    missing = [b for b in updated if b not in b2b]

    save_csv("NEEGZbarmarini.csv", missing)
    print(f"Sukurta: NEEGZbarmarini.csv ({len(missing)} barkodų)")

    print("Darbas baigtas.")


if __name__ == "__main__":
    main()

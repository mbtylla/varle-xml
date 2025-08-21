import xml.etree.ElementTree as ET

# 1. Perskaitome zuja.xml
zuja_tree = ET.parse("zuja.xml")
zuja_root = zuja_tree.getroot()

# 2. Sukuriame žemėlapį: barcode -> total_quantity
quantities = {}
for product in zuja_root.findall(".//product"):
    barcode = product.findtext("barcode")
    total_quantity = product.findtext("total_quantity")
    if barcode and total_quantity is not None:
        quantities[barcode] = total_quantity

print(f"Rasta {len(quantities)} įrašų zuja.xml")

# 3. Perskaitome updated_products.xml
tree = ET.parse("updated_products.xml")
root = tree.getroot()

# 4. Atnaujiname <quantity> pagal barcode
count_updated = 0
for product in root.findall(".//product"):
    barcode = product.findtext("barcode")
    if barcode in quantities:
        quantity_el = product.find("quantity")
        if quantity_el is not None:
            quantity_el.text = quantities[barcode]
            count_updated += 1

print(f"Atnaujinta {count_updated} prekių quantity laukelių")

# 5. Išsaugome atnaujintą failą
tree.write("updated_products.xml", encoding="utf-8", xml_declaration=True)

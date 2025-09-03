import requests
from datetime import datetime

URL = "https://marini.pl/b2b/marini-b2b.xml"
LOCAL_FILE = "marini-b2b.xml"

def download_file():
    print("[INFO] Parsisiunčiamas XML failas...")
    r = requests.get(URL)
    r.raise_for_status()
    with open(LOCAL_FILE, "wb") as f:
        f.write(r.content)
    print("[INFO] Failas sėkmingai parsisiųstas:", LOCAL_FILE)

if __name__ == "__main__":
    download_file()
    with open("LAST_UPDATE.txt", "w") as f:
        f.write(f"Atnaujinta: {datetime.now()}\n")


import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def get_nand_price():
    url = "https://www.trendforce.com.tw/price/flash/flash_spot"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", class_="price-table")

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    data = []
    for row in table.find_all("tr")[1:]:
        cols = row.find_all("td")
        product_name = cols[0].text.strip()
        avg_price = cols[5].text.strip()
        price_change = cols[6].text.strip()
        
        if "SLC 2Gb 256MBx8" in product_name or "SLC 1Gb 128MBx8" in product_name or "MLC 64Gb 8GBx8" in product_name or "MLC 32Gb 4GBx8" in product_name:
            data.append([now, product_name, avg_price, price_change])

    df = pd.DataFrame(data, columns=["Timestamp", "Product", "Average Price", "Price Change"])
    
    try:
        existing_df = pd.read_csv("nand_prices.csv")
        df = pd.concat([existing_df, df], ignore_index=True)
    except FileNotFoundError:
        pass

    df.to_csv("nand_prices.csv", index=False)
    print(f"Successfully scraped and saved data at {now}")

if __name__ == "__main__":
    get_nand_price()

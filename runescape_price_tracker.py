
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random

headless = False

chrome_options = Options()
if headless:
    chrome_options.add_argument("--headless=new")  # Required for newer versions (Chrome 109+)
else:
    chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--ignore-ssl-errors")
driver = webdriver.Chrome(options=chrome_options)

base_url = "https://runescape.wiki"

driver.get(base_url)
time.sleep(random.uniform(2, 5))

def get_item_price(item_name):
    try:
        wait = WebDriverWait(driver, 15)  # Increased wait time

        # Go directly to the item page instead of using search
        driver.get(f"https://runescape.wiki/w/{item_name.replace(' ', '_')}")
        time.sleep(random.uniform(3, 6))  # Random delay to avoid detection

        # Wait until the price element is visible
        price_element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "infobox-quantity-replace")))
        
        price = price_element.text.replace(",", "")
        return int(price)

    except Exception as e:
        print(f"Error getting price for {item_name}: {e}")
        return "Not Tradable on Grand Exchange"

file_path = "Watchprice.xlsx"
df = pd.read_excel(file_path)
items = df["Item Name"].tolist()
buyPrices = df["Buy Price"].tolist()
sellPrices = df["Sell Price"].tolist()

priceData = []
for i in range(len(items)):
    itemName = items[i]
    buyPrice = buyPrices[i]
    sellPrice = sellPrices[i]
    
    currentPrice = get_item_price(itemName)
    
    if isinstance(currentPrice, int):
        if currentPrice < buyPrice:
            action = "BUY"
        elif currentPrice > sellPrice:
            action = "SELL"
        else:
            action = "HOLD"

        priceData.append({
            "Item": itemName,
            "Current Price": currentPrice,
            "Buy Price": buyPrice,
            "Sell Price": sellPrice,
            "Action": action
        })
    else:
        priceData.append({
            "Item": itemName,
            "Current Price": "N/A",
            "Buy Price": "N/A",
            "Sell Price": "N/A",
            "Action": "N/A"
        })
        
output_df = pd.DataFrame(priceData)
output_df.to_csv("runescape_price_recommendations.csv", index=False)

print(output_df)

driver.quit()

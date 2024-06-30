"""
Scrapes airbnb .csv links from Inside Airbnb.

Author: Hanna Scharinger
Version: 2024/06
"""
# --------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------
import time
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from modules.general_function import get_driver


# --------------------------------------------------------------------
# Functions definition
# --------------------------------------------------------------------
def scrape_airbnb_csv_links(city, country):
    """
    Scrapes airbnb csv links from web page for Vienna
    :returns: 4 links of the last 4 quarters
    """
    driver = get_driver()
    # navigate to website
    driver.get('https://insideairbnb.com/get-the-data/')

    # wait until all results are loaded
    wait = WebDriverWait(driver, 2)

    # search for the 'show' button from Vienna
    button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'.showArchivedData[data-city="{city}"]')))
    time.sleep(2)
    # click the button to load all 4 links
    driver.execute_script("arguments[0].click();", button)

    # save page source
    page_source = driver.page_source
    driver.quit()

    #
    soup = BeautifulSoup(page_source, 'html.parser')
    links = soup.find_all('a', href=True, string='listings.csv.gz')

    vienna_links = []
    for link in links:
        url = link.get('href')
        city = city.lower()
        country = country.lower()
        if f'{city}' and f'{country}' in url:
            vienna_links.append(url)

    return vienna_links


if __name__ == '__main__':
    """
    This is executed only when this file is executed directly.
    """
    urls_vienna_listings = scrape_airbnb_csv_links('Vienna', 'Austria')
    print(urls_vienna_listings)

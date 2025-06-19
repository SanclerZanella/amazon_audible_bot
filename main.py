import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# URLs
main_url = "https://www.audible.co.uk/charts/best?ref_pageloadid=not_applicable&plink=j69JEv4NjcdOwuVT&pageLoadId=EcHdt1sz3vhmAiTR&creativeId=209a9396-a0bd-443c-93ab-d608f0c4ed36&ref=a_search_t1_navTop_pl0cg1c0r0"
path = r'assets\chromedriver-win64\chromedriver.exe'

# Browser options
options = Options()
options.add_argument('window-size=1920x1080')
# options.add_argument('--headless=new')

# Initialise browser
service = Service(path)
driver = webdriver.Chrome(service=service, options=options)
driver.get(main_url)
driver.maximize_window()

time.sleep(3)

# Resolve consent data overlay
# consent_data_overlay = driver.find_element(By.XPATH, '//div[@id="truste-consent-buttons"]')
consent_data_overlay = WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.XPATH, '//div[@id="truste-consent-buttons"]')))
accept_btn = consent_data_overlay.find_element(By.XPATH, 'button[@id="truste-consent-button"]')
accept_btn.click()

# Pagination
pagination = driver.find_element(By.XPATH, '//ul[contains(@class, "pagingElements")]')
pages = pagination.find_elements(By.XPATH,'li')
last_page = int(pages[-2].text)

# Move through the pages
current_page = 1

# Store audibles info for dataframe creation
audible_titles = []
audible_authors = []
audible_lengths = []

while current_page <= last_page:
    time.sleep(2)
    # Get column list of audibles
    # audibles_column = driver.find_element(By.XPATH, '//div[@class="adbl-impression-container "]')
    audibles_column = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//div[@class="adbl-impression-container "]')))

    # Get each audible
    # audibles = audibles_column.find_elements(By.XPATH, './/li[contains(@class, "productListItem")]')
    audibles = WebDriverWait(audibles_column, 5).until(
        EC.presence_of_all_elements_located((By.XPATH, './/li[contains(@class, "productListItem")]')))

    # Get each audible title, authors and length
    for audible in audibles:
        # Get the audible title
        # title_header = audible.find_element(By.XPATH, './/h3[contains(@class, "bc-heading")]')
        title_header = WebDriverWait(audible, 5).until(
            EC.presence_of_element_located((By.XPATH, './/h3[contains(@class, "bc-heading")]')))

        title_link = WebDriverWait(title_header, 10).until(
            EC.presence_of_element_located((By.XPATH, './a')))

        audible_titles.append(title_link.text)

        # Get the audible authors
        authors = []
        # author_li = audible.find_element(By.XPATH, './/li[contains(@class, "authorLabel")]')
        author_li = WebDriverWait(audible, 5).until(
            EC.presence_of_element_located((By.XPATH, './/li[contains(@class, "authorLabel")]')))

        # author_links = author_li.find_elements(By.XPATH, './/a')
        author_links = WebDriverWait(author_li, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, './/a')))

        for author_link in author_links:
            authors.append(author_link.text)

        audible_authors.append(', '.join(authors))

        # Get the length
        # length_li = audible.find_element(By.XPATH, './/li[contains(@class, "runtimeLabel")]')
        length_li = WebDriverWait(audible, 5).until(
            EC.presence_of_element_located((By.XPATH, './/li[contains(@class, "runtimeLabel")]')))
        audible_lengths.append(length_li.find_element(By.XPATH, './span').text)

    # Move to the next page
    current_page += 1

    try:
        next_page_btn = driver.find_element(By.XPATH, '//span[contains(@class, "nextButton")]')
        next_page_btn.click()
    except:
        pass

# Close browser
driver.quit()

# Convert collected date to dataframe and csv
df_books = pd.DataFrame({
    'Title': audible_titles,
    'Author': audible_authors,
    'Length': audible_lengths,
})

df_books.to_csv('audibles.csv', index=False)

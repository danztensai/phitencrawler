from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import urllib.request
import os
import re
import shutil
from urllib.parse import urlparse

def create_directory(name):
    # Create target directory & all intermediate directories if don't exists
    dirName = name
    try:
        os.makedirs(dirName)    
        print("Directory " , dirName ,  " Created ")
    except FileExistsError:
        print("Directory " , dirName ,  " already exists")  

def move_file(source, destination):
    try:
        isFile = os.path.isfile(destination)
        if not os.path.isfile(destination):
            shutil.move(source, destination)
        else:
            os.remove(destination)
    except shutil.Error:
        print("Something Wrong when try to move")

def uri_validator(x):
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc, result.path])
    except:
        return False

chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--disable-gpu')
# chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("window-size=1900,1080")
capabilities = chrome_options.to_capabilities()
driver = webdriver.Chrome(options=chrome_options)
driver.get("http://www.phiteneurope.com/en")
nav_menu = driver.find_element_by_css_selector('ul.menu.nav')
nav_link = [link.get_attribute("href") for link in nav_menu.find_elements_by_tag_name('a')]
root_folder = 'crawl_phiteneurope/'
create_directory(root_folder)
for n in nav_link:
    print(n.split('/')[-1])
    folder_nav = root_folder + re.sub(r'\W+', '', n.split('/')[-1])
    create_directory(folder_nav)
    url = n
    driver.get(url)
    SCROLL_PAUSE_TIME = 0.5

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    product_list = driver.find_elements_by_xpath('//*[@id="product-list-container"]/div/div/article/a')
    product_link = [p.get_attribute('href') for p in product_list]
    for prod_link in product_link:
        print('This Is product',prod_link)
        driver.get(prod_link)
        print(driver.title)
        image_list = driver.find_elements_by_xpath('//*[@id="product-details-page"]//img')
        image_link = [img.get_attribute('src') for img in image_list]
        title = driver.find_element_by_xpath('//*[@id="product-details"]/div/div/div/div/div/header/h1')
        price = driver.find_element_by_css_selector('span.PricesalesPrice').get_attribute("innerHTML")
        main_image_link = driver.find_element_by_xpath('//*[@id="zoom1"]').get_attribute('href')
        main_image_filename = main_image_link.split('/')[-1]
        product_code = main_image_filename.split('_')[0]

        product_description_element = driver.find_element_by_xpath('//*[@class="tab-content"]')
        with open("description.txt", "w") as text_file:
            print(f"Product Name : {title.text} \n", file= text_file)
            print(f"Product Code : {product_code}\n", file=text_file)
            print(f"Product Price : {price}\n", file=text_file)
            print(f"Description : \n {product_description_element.text} \n ", file=text_file)
        
        product_name_folder = folder_nav+'/'+title.text.split('/')[-1].strip()
        create_directory(product_name_folder)
        move_file("description.txt",product_name_folder)
        print(image_link)
        for image in image_link:
            if uri_validator(image):
                filename = image.split('/')[-1]
                print('Downloading Image ',filename)
                urllib.request.urlretrieve(image, filename)
                print('Finished Download', filename)
                move_file(filename, product_name_folder)

driver.close()


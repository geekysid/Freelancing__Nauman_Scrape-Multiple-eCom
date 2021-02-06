#!/usr/local/bin/python3


# # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                       #
#   Name: Siddhant Shah                                 #
#   Date: 06/02/2021                                    #
#   Desc: SCRAPER FOR PRICE FROM MULTIPLE SOURCE        #
#   Email: siddhant.shah.1986@gmail.com                 #
#                                                       #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from colorama import init
from termcolor import cprint
import time, json, os, sys


# global variables
DATA = {}
CONFIG_DATA = {}
WAIT_TIME = 10
BROWSER = None


# just fro decoration
def intro_deco():
    print("\n\n")
    print("  ", '#'*46)
    print("  ", "#                                            #")
    print("  ", "#   SCRAPER FOR PRICE FROM MULTIPLE SOURCE   #")
    print("  ", "#              By: SIDDHANT SHAH             #")
    print("  ", "#                Dt: 06-02-2021              #")
    print("  ", "#        siddhant.shah.1986@gmail.com        #")
    print("  ", "#      **Just for Educational Purpose**      #")
    print("  ", "#                                            #")
    print("  ", '#'*46)
    print()


# getting information from config file
def initializer():
    global CONFIG_DATA

    if os.path.exists(f'{os.getcwd()}/config_selector.json'):
        with open (f'{os.getcwd()}/config_selector.json', 'r') as r:
            CONFIG_DATA = json.load(r)


# Setting up webdriver
def get_browser(headless=False):

    pathToChromeDriver = CONFIG_DATA['pathToChromeDriver']

    chrome_options = Options()

    # giving a higher resolution to headless browser so that click operation works
    if headless:
        chrome_options.headless = headless
    else:
        chrome_options.add_argument('--window-size=1920,1080')
        # chrome_options.add_argument("--start-maximized")

    browser = webdriver.Chrome(executable_path = pathToChromeDriver, options=chrome_options)

    return browser


# getting element from config
def get_element(selector, base=''):
    base = BROWSER if (base == '') else base
    selector_type = list(selector.keys())[0]

    try:
        if selector_type == 'class':
            return base.find_element_by_class_name(selector[selector_type])
        elif selector_type == 'id':
            return base.find_element_by_id(selector[selector_type])
        elif selector_type == 'attribute':
            selector_tag =selector[list(selector.keys())[1]]
            return base.find_element_by_xpath(f"//{selector_tag}[{selector[selector_type]}]")
        elif selector_type == 'tag_name':
            return base.find_element_by_tag_name(selector[selector_type])
        elif selector_type == 'xpath':
            return base.find_element_by_xpath(selector[selector_type])
    except Exception as err:
        # cprint(f'    [x] Exeption: Can\'t locate selector. \n{str(err)}', 'red', attrs=['bold'])
        pass


# getting elements from config
def get_elements(selector, base=''):

    base = BROWSER if (base == '') else base
    selector_type = list(selector.keys())[0]

    if selector_type == 'class':
        return base.find_elements_by_class_name(selector[selector_type])
    if selector_type == 'id':
        return base.find_elements_by_id(selector[selector_type])
    if selector_type == 'tag_name':
        return base.find_elements_by_tag_name(selector[selector_type])


# waiting for certain element on page to load
def page_load_wait(selector):
    selector_type = list(selector.keys())[0]

    try:
        if selector_type == 'id':
            WebDriverWait(BROWSER, WAIT_TIME).until(EC.visibility_of_element_located((By.ID, selector[selector_type])))
        if selector_type == 'xpath':
            WebDriverWait(BROWSER, WAIT_TIME).until(EC.visibility_of_element_located((By.XPATH, selector[selector_type])))
        return True
    except Exception as err:
        cprint(f'    [x] Exception while waiting for page to load.', 'red', attrs=['bold'])
        cprint(f'    [x] Exception: {str(err)}', 'red', attrs=['bold'])
        return False


# saving fetched data into json file
def save_json(website):
	with open(f'Data/{website}.json', 'w') as file:
		json.dump(DATA, file)


# get individual product data
def get_product_data(product_link, selector, product_count):
    BROWSER.get(product_link)
    product_heading = get_element(selector['product_name']).text
    cprint(f'          [{product_count}] {product_heading}', 'green', attrs=['bold'])

    product = {}
    product['url'] = BROWSER.current_url
    retail_EAN = None

    product_table = get_element(selector['individual_prod'])
    product_desp_rows = get_elements(selector['indv_prod_desc_rows'], product_table)

    for product_desp in product_desp_rows:
    	key = get_element(selector['indv_prod_key'], product_desp).text.strip().replace(':', '')
    	value = get_element(selector['indv_prod_value'], product_desp).text.strip()
    	if key == 'Retail EAN':
    		retail_EAN = value
    	cprint(f'              [>>] {key}: {value}', 'yellow', attrs=['bold'])

    	product[key] = value

    product_image = get_element(selector['indv_prod_image'])
    if product_image:
    	product['image'] = product_image.get_attribute('href')

    print()

    return (retail_EAN, product)


# retrieve oil prices
def get_products(selectors, product_links):
    products_container = get_element(selectors['products_container'])
    products = get_elements(selectors['products'], base=products_container)
    prod_count = 1

    for product in products:
        if product.get_attribute("class") == 'hiddencol':
            continue
        product_link_div = get_element(selectors['product_link_div'], base=product)
        product_link_url = get_element(selectors['product_link'], base=product_link_div).get_attribute('href')
        # product_link_img = get_element(selectors['product_img'], base=product_link_div).get_attribute('src')

        # product_name = get_element(selectors['product_name'], base=product).text.strip()
        # product_sku = get_element(selectors['product_sku'], base=product).text.strip().split('SKU: ')[-1]
        # product_size = get_element(selectors['product_size'], base=product).text.strip()
        # product_rsp = get_element(selectors['product_rsp'], base=product).text.strip().split('RSP: ')[-1]
        # product_promotion = get_element(selectors['product_promotion'], base=product).text.strip()

        # cprint(f'          [{prod_count}] {product_name}', 'yellow', attrs=['bold'])
        # cprint(f'              [>>] SKU: {product_sku}', 'yellow', attrs=['bold'])
        # cprint(f'              [>>] Size: {product_size}', 'yellow', attrs=['bold'])
        # cprint(f'              [>>] RSP: {product_rsp}', 'yellow', attrs=['bold'])
        # # cprint(f'              [>>] Promotion: {product_sku}, 'yellow', attrs=['bold'])
        # cprint(f'              [>>] URL: {product_link_url}', 'yellow', attrs=['bold'])
        # cprint(f'              [>>] Image: {product_link_img}', 'yellow', attrs=['bold'])
        # print()
        product_links.append(product_link_url)
        prod_count += 1

    cprint(f'          [>>] Fetched {prod_count} products', 'yellow', attrs=['bold'])
    cprint(f'          [>>] Total {len(product_links)} products\n', 'yellow', attrs=['bold'])
    return product_links


# click on next page button if available
def go_to_next_page(selectors, page_count):
    next_btn = get_element(selectors['next_btn'])
    if next_btn:
        cprint(f'\n      [+] Going to Next # {page_count}', 'magenta', attrs=['bold'])
        next_btn.click()
        return True
    else:
        return False


# getting products depending on category
def get_category_data(website):
    global DATA
    DATA[website] = {}

    config = CONFIG_DATA['website'][website]
    selectors = config['selectors']

    # looping for different categories
    for category_config in config['categories']:
        category_url = category_config['category_url']
        category = category_config['category']
        DATA[website][category] = {}
        cprint(f'      [>] Category: {category.upper()}', 'cyan', attrs=['bold'])

        # going to base url
        BROWSER.get(category_url)

        # select 100 from dropdown
        try:
            get_element(selectors['item_per_page']).send_keys('100')
            time.sleep(1)
        except Exception as error:
            cprint(f'      [x] EXCEPTION: {str(error)}', 'red', attrs=['bold'])

        page_count = 2
        product_links = []

        # getting all products for given category
        while True:
            if page_count % 4 == 0:
            	break
            if page_load_wait(selectors['home_page_load_wait']):
                product_links = get_products(selectors, product_links)    # getting all products link in this category
                next_page = go_to_next_page(selectors, page_count)    # goin to next page

                if not next_page:
                    break;
                else:
                    page_count += 1
            else:
                cprint('        [x] Unable to load the page', 'red', attrs=['bold'])
                break

        print()

        # getting data of inidividual product
        product_count = 1
        for product_link in product_links:
            retail_EAN, product = get_product_data(product_link, selectors, product_count)
            DATA[website][category][retail_EAN] = product
            product_count += 1
            save_json(website)


# getting required data from website
def get_required_data():
    for website in CONFIG_DATA['website'].keys():
        cprint(f'  [+] {website.upper()}', 'blue', attrs=['bold'])
        get_category_data(website)


# executing script only if its not imported
if __name__ == '__main__':
    try:
        init()
        intro_deco()
        initializer()
        BROWSER = get_browser(headless=False)
        get_required_data()
        BROWSER.quit()
    except Exception as error:
        cprint(f'  [x] EXCEPTION: {str(error)}', 'red', attrs=['bold'])
        input()
        if BROWSER:
            BROWSER.quit()

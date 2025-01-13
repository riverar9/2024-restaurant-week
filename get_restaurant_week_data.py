# %%
import os
import time
import json

default_sleep_duration = 0.000

current_season = '2025_winter'

json_file_path = f"{current_season}_all_restaurants.json"

# Load dictionary from file or create an empty one
def load_dict(file_path = json_file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def update_dict(key, value, file_path = json_file_path):
    data_dict = load_dict(file_path)
    data_dict[key] = value
    with open(file_path, 'w') as file:
        json.dump(data_dict, file, indent=4)

def get_latest_chrome_driver():
    # Install the driver:
    # Downloads ChromeDriver for the installed Chrome version on the machine
    # Adds the downloaded ChromeDriver to path
    from get_chrome_driver import GetChromeDriver

    # Delete the directory if it exists

    print('Downloading Chromedriver...')
    get_driver = GetChromeDriver()
    get_driver.install()
    print('\tChromedriver Downloaded.')

def find_chromedriver(starting_directory = '.'):
    # Searches for 'chromedriver.exe' starting from the specified directory.
    
    for root, dirs, files in os.walk(starting_directory):
        if 'chromedriver.exe' in files:
            return os.path.join(root, 'chromedriver.exe')
    return None

def open_website(url, chrome_driver_downloaded = False):
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By

    chrome_options = Options()
    #chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
    
    # Path to chromedriver
    if not chrome_driver_downloaded:
        get_latest_chrome_driver()
    chromedriver_path = find_chromedriver()
    
    # Check if chromedriver exists
    if not os.path.isfile(chromedriver_path):
        print(f"Error: chromedriver not found at {chromedriver_path}")
        return

    # Set up WebDriver
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(url)

    # Click on the cookies element
    cookies_element = driver.find_element(By.CSS_SELECTOR, '[aria-label="Accept cookies"]')
    cookies_element.click()

    print('\tWebsite Open.')

    return driver

def open_page_websites(driver, source_tab_handle):
    from selenium.webdriver.common.by import By

    # Get the list of items on this page
    time.sleep(default_sleep_duration)
    container_name = "PromotionCardGrid_container__phhU9"
    parent_element = driver.find_element(By.CLASS_NAME, container_name)

    children_elements = parent_element.find_elements(By.XPATH, './*')

    # Click on each tile and move back to the root tab
    for each_child in children_elements:
        # Click on it
        each_child.click()
        time.sleep(default_sleep_duration)
        driver.switch_to.window(source_tab_handle)
        time.sleep(default_sleep_duration)

def move_to_next_page(driver):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.action_chains import ActionChains

    pagination_class_name = "PromotionCardGrid_pagination__g0F_c"
    
    pagination_element = driver.find_element(By.CLASS_NAME, pagination_class_name)
    page_number_elements = pagination_element.find_elements(By.XPATH, ".//a")
    page_numbers = [int(el.text) for el in page_number_elements if el.text.isdigit()]

    # The last page will have the below properties. If we're on the last page then don't click
    if page_numbers == [1, 49]:
        print('\tOn the last page. Skipping')
        return False
    else:
        actions = ActionChains(driver)
        
        next_page_element = driver.find_element(By.CLASS_NAME, "next")

        actions.move_to_element(next_page_element)
        next_page_element.click()
        return True

def save_restaurant_information(driver, tab_to_mine, debug = False):
    from selenium.webdriver.common.by import By
    
    # Swith to the restaurant's tab incase it wasn't done already
    driver.switch_to.window(tab_to_mine)

    # Set up all single value responses
    class_mine_list = [
        ('restaurant_name', 'HotelDetailPage_termsDetail__bcmpP')
        , ('restaurant_address', 'QuickInfo_locationAddressContainer__UhWNN')
        , ('restaurant_description', 'RichText_richTextWrapper__FifG2')
        #, ('restaurant_url', 'QuickInfo_link__LF7_N Link_link__r_cmh Link_linkFonts__L1392')
    ]
    
    # Set up multiple value responses.
    week_deal_class_id = "RestaurantWeekTag_inclusionWeek__SZfru"
    
    # Set up an empty dictionary to collect responses
    t_dict = {
        'restaurant_week_url' : driver.current_url
    }

    # Collect the single value responses
    for each_css_element in class_mine_list:
        try:
            t_dict[each_css_element[0]] = driver.find_element(By.CLASS_NAME, each_css_element[1]).text
            if debug:
                print(f"\t\tDB: {t_dict[each_css_element[0]]}")
        except:
            t_dict[each_css_element[0]] = 'N/A'

    # Create two temporary lists for the multiple value responses
    t_dict['weeks'] = []
    t_dict['deals'] = []

    try:
        for each_week_deal in driver.find_elements(By.CLASS_NAME, week_deal_class_id):
            if each_week_deal.text.startswith('Week'):
                t_dict['weeks'].append(each_week_deal.text)
            elif each_week_deal.text.startswith('$'):
                t_dict['deals'].append(each_week_deal.text)
    except:
        t_dict['weeks'] = ['N/A']
        t_dict['deals'] = ['N/A']

    try:
        t_dict['restaurant_url'] = driver.find_element(By.XPATH, "//a[@aria-label='visit website link']").get_attribute("href")
        if debug:
            print(f"DB: {t_dict['restaurant_url']}")
    except:
        t_dict['restaurant_url'] = 'N/A'
    
    update_dict(
        t_dict['restaurant_name'],
        t_dict
    )

    print(f"\tDownloaded data for '{t_dict['restaurant_name']}'")

 # %%
def main():
    # Set up the restaurant week url
    restaurant_week_url = "https://www.nyctourism.com/restaurant-week/"
    
    driver = open_website(restaurant_week_url, chrome_driver_downloaded=True)
    source_tab_handle = driver.current_window_handle

    # Set up a loop iteration variable
    loop_iteration = 0
    not_last_page = True
    while not_last_page:
        # Switch to the source page
        driver.switch_to.window(source_tab_handle)
        
        # Increment the loop
        loop_iteration += 1
        print(f"On Page: {loop_iteration}")

        # Check the loop iteration to see if we need to go to the next page.
        #   The function move_to_next_page returns true or false if we're on the last page.
        if loop_iteration > 1:
            not_last_page = move_to_next_page(driver)
        
        # Open the driver
        open_page_websites(driver, source_tab_handle)
        
        for each_open_tab in driver.window_handles:
            if each_open_tab != source_tab_handle:
                driver.switch_to.window(each_open_tab)
                save_restaurant_information(driver, each_open_tab)
                driver.close()
# %%
if __name__ == "__main__":
    main()
# %%
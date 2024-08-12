# %%
import os
import time

default_sleep_duration = 0.250

def get_latest_chrome_driver():
    # Install the driver:
    # Downloads ChromeDriver for the installed Chrome version on the machine
    # Adds the downloaded ChromeDriver to path
    from get_chrome_driver import GetChromeDriver

    # Delete the directory if it exists

    print('\tDownloading Chromedriver...')
    get_driver = GetChromeDriver()
    get_driver.install()
    print('\t\tChromedriver Downloaded.')

def find_chromedriver(starting_directory = '.'):
    """
    Searches for 'chromedriver.exe' starting from the specified directory.
    
    :param starting_directory: Directory to start the search from
    :return: Path to the 'chromedriver.exe' file if found, otherwise None
    """
    for root, dirs, files in os.walk(starting_directory):
        if 'chromedriver.exe' in files:
            return os.path.join(root, 'chromedriver.exe')
    return None

def open_website(url):
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options

    chrome_options = Options()
    #chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
    
    # Path to chromedriver
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

    print('\tWebsite Open.')

    return driver

def open_page_websites(driver):
    from selenium.webdriver.common.by import By

    # Get the list of items on this page
    time.sleep(default_sleep_duration)
    container_name = "PromotionCardGrid_container__1jhJo"
    parent_element = driver.find_element(By.CLASS_NAME, container_name)

    children_elements = parent_element.find_elements(By.XPATH, './*')

    # Document the source tab
    source_tab_handle = driver.current_window_handle

    # Click on each tile and move back to the root tab
    for each_child in children_elements:
        # Click on it
        each_child.click()
        time.sleep(default_sleep_duration)
        driver.switch_to.window(source_tab_handle)
        time.sleep(default_sleep_duration)

# %%
def main():
    a = open_website('https://www.nyctourism.com/restaurant-week/')
    open_page_websites(a)
# %%
main()
# %%

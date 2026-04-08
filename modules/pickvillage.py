from concurrent.futures import wait

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import re
import pandas as pd
from tqdm import tqdm

import pandas as pd
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def village_chose(wait, driver):
    """Chooses the village to make the atack after ended the trops"""
    data = []

    all_villages_xpath = '//*[@id="sidebarBoxVillageList"]/div[2]/div[2]/div'
    
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, all_villages_xpath)))
        village_containers = driver.find_elements(By.XPATH, all_villages_xpath)
        print(f"Found {len(village_containers)-1} villages.")
    except Exception as e:
        print(f"Error finding villages or page timeout: {e}")
    
    for index, container in enumerate(village_containers[1:], start=1):
        try:
            #Village name
            village_name = container.find_element(By.XPATH, './div/a/div/span[2]').text

            # Get the specific_xpath
            specific_click_xpath = f'{all_villages_xpath}[{index}]/div/a'

            # Store in a dict
            data.append({
                "Village_number": index,
                "Village_Name": village_name,
                "Village_Link": specific_click_xpath
            })

        except Exception as e:
            print(f"Error processing village #{index}: {e}")
            continue

    # 4. Create DataFrame and print results
    df_village_table = pd.DataFrame(data)


    return df_village_table

def click_village(wait, village_number):
    # Click Village button
    village_number +=1
    village_button = wait.until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="sidebarBoxVillageList"]/div[2]/div[2]/div[{village_number}]/div/a')))
    village_button.click()
    return

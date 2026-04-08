# ataque.py
from concurrent.futures import wait

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import re
import pandas as pd
import tqdm



def input_cords(driver, wait, cord_x, cord_y, lista):
                """Input the coordinates in the respective fields and click the button to refresh the page with the coordinates"""
                
                
                # add village to farmlist
                print(f"Adding coordinates to the farmlist: {lista}")
                time.sleep(2)
                # Click over the button "add target" of the respective list
                add_twon = wait.until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="rallyPointFarmList"]//div[@data-sortindex="{lista}"]//td[@class="addTarget"]//a')))
                
                # Scroll in case the button is out of the screen
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_twon)
                time.sleep(1)
                add_twon.click()
                print(f"   ✓ Clicked the 'Add target' button for coordinates. ({cord_x}|{cord_y}).")
                
                # Input coordinates and click get refresh with a clear XPATH on box of trop colonizer
                x_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="farmListTargetForm"]/div[2]/div[1]/label[2]/input')))
                x_input.clear()
                x_input.send_keys(str(cord_x))
                y_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="farmListTargetForm"]/div[2]/div[1]/label[3]/input')))
                y_input.clear()
                y_input.send_keys(str(cord_y))
                get_refrash = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="farmListTargetForm"]/div[3]/label[10]/input')))
                get_refrash.click()
                
                # Check for error messages related to coordinates and handle them if they appear
                try:
                    erro = WebDriverWait(driver, 2).until(
                         EC.any_of(
                                 EC.visibility_of_element_located((By.XPATH, '//*[@id="build"]/div/p')), # Erro genérico
                                 EC.visibility_of_element_located((By.XPATH, '//*[@id="farmListTargetForm"]/div[2]/div[2]/div[1]')) # Erro Não há nenhuma aldeia nestas coordenadas
                                 ))

                    if erro.text is not None:
                        print(f" Something is wrong with the coordinates. ({cord_x}|{cord_y}).")
                        cancel_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="farmListTargetForm"]/div[5]/button[1]')))
                        cancel_button.click()
                        return 

                except TimeoutException:
                    # If nothing appears, just continue with the process
                    pass
                
                # Click on save button
                save_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="farmListTargetForm"]/div[5]/button[2]')))
                save_button.click()
                time.sleep(2)

                # Check for error messages related to duplicate entries and handle them if they appear
                try:
                    
                    dial_msg = WebDriverWait(driver, 6).until(
                        EC.visibility_of_element_located((By.XPATH, '//*[@id="dialogContent"]/div/div/p'))
                    )
                    # if duplicate entry error appears, it means the village is already in the farm list, so we just click ok to add it again and move on to the next one
                    if dial_msg.text:
                        print(f"  ⚠ Village ({cord_x}|{cord_y}) already exists in the farm list. Skipping...")
                        
                        # Click OK
                        ok_button = wait.until(
                            EC.element_to_be_clickable((By.XPATH, '//*[@id="dialogContent"]/div/button[2]'))
                        )
                        ok_button.click()

                except TimeoutException:
                    # No duplicate entry error, so we assume the village was added successfully
                    print(f"   ✓ Village ({cord_x}|{cord_y}) successfully added to the farmlist.")
                    pass

def farmlist(driver, wait, df_inact):
    """Open the farmlist page and add the villages from the dataframe to the respective lists based on their population"""
    
    print("Opening Farmlist...")
    driver.get("https://ts10.x1.europe.travian.com/build.php?id=39&gid=16&tt=99")
    print("   ✓ Farmlist opened, starting to add targets...")
    time.sleep(2)
    for x in tqdm(range(len(df_inact))):
        cord_x = df_inact.iloc[x]['X']
        cord_y = df_inact.iloc[x]['Y']

        # Check if the tabs are expanded and if so, colapse them
        expanded = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="rallyPointFarmList"]/div[1]/div[1]')))
        if expanded.get_attribute("class") == "villageHeader expanded":
            colapse_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="rallyPointFarmList"]/div[1]/div[1]/a')))
            print("   ✓ Colapse button found, clicking to open category...")
            colapse_button.click()
        
        time.sleep(1)
        print(df_inact.iloc[x]["População"])


        # The "lista" variable is used to determine which tab of the farmlist we will add the village to, 
        # Since there are 3 tabs for different population ranges, we need to specify which one we want to add the village to.

        # The "expanded_button" variable is used to expand the category of the farmlist where we will add the village, 
        # Since only one category can be expanded at a time because of size window, we need to expand the correct one before adding the village.
        if df_inact.iloc[x]['População'] > 250:
            lista = "1"
            expanded_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="rallyPointFarmList"]/div[1]/div[2]/div/div[1]/a')))
            expanded_button.click()
            print(f"   ✓ Village in ({cord_x}|{cord_y}) with population {df_inact.iloc[x]['População']} classified as a large city.")
            input_cords(driver, wait, cord_x, cord_y, lista)
            print(f"   ✓ Village in ({cord_x}|{cord_y}) added to the farmlist of large cities.")

        
        elif df_inact.iloc[x]['População'] >= 100 and df_inact.iloc[x]['População'] <= 250:
            lista = "2"
            expanded_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="rallyPointFarmList"]/div[1]/div[3]/div/div[1]/a')))
            expanded_button.click()
            print(f"   ✓ Village in ({cord_x}|{cord_y}) with population {df_inact.iloc[x]['População']} classified as a medium city.")
            input_cords(driver, wait, cord_x, cord_y, lista)
            print(f"   ✓ Village in ({cord_x}|{cord_y}) added to the farmlist of medium cities.")


        elif df_inact.iloc[x]['População'] > 0 and df_inact.iloc[x]['População'] < 100:
            lista = "3"
            expanded_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="rallyPointFarmList"]/div[1]/div[4]/div/div[1]/a')))
            expanded_button.click()
            print(f"   ✓ Village in ({cord_x}|{cord_y}) with population {df_inact.iloc[x]['População']} classified as a small city.")
            input_cords(driver, wait, cord_x, cord_y, lista)
            print(f"   ✓ Village in ({cord_x}|{cord_y}) added to the farmlist of small cities.")

    return print("## Farmlist updated successfully! ##")
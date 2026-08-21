# ataque.py
from concurrent.futures import wait

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import re
import pandas as pd
from tqdm import tqdm
import os
import json

# File to save the names of the lists in the farmlist, so we can find them later and add the villages to the correct list
FILE = "data/list_names.json"

# List of names for the farmlist categories, we will load this from a json file later
# Keep in mind that the list may change with the gameslist, so if you start a new game you may need to update the list
# to the standard names removing the suffixes "-1".

# Variables information "lista" #
# is the position of the list in the farmlist game for exemple if list pop 100 - 250 is in the 1st row
# lista is taking value 2 since 1st row is the header of container with the name of the village.
# Variables information "lista2" #
# Is the number of villages in the list, for example if list pop 100 - 250 has 10 villages, lista2 is taking value 10.

def colapse(driver, wait):
    rally_pointfarmlist = wait.until(EC.presence_of_element_located((By.ID, "rallyPointFarmList")))
    village_wrappers = rally_pointfarmlist.find_elements(By.CLASS_NAME, "villageWrapper")

    for village_wrapper in village_wrappers:
        expanded_headers = village_wrapper.find_elements(By.CSS_SELECTOR, ".villageHeader.expanded")
        if expanded_headers:
            expand_collapse = expanded_headers[0].find_element(By.CLASS_NAME, "expandCollapse")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", expand_collapse)
            wait.until(EC.element_to_be_clickable(expand_collapse)).click()

def expand_colapse(driver, wait, dropContainer):
        """Funtion to expand or colapse the dropContainer"""
        expand_collapse = dropContainer.find_element(By.CLASS_NAME, "expandCollapse")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", expand_collapse)
        expanded = wait.until(EC.element_to_be_clickable(expand_collapse))
        expanded.click()
        time.sleep(2)
        return

def list_control(listdic, farm_name_list):
        r"""Verifies if farm_name_list has a match with listdic.
    If there is a match, add a suffix " - (\d+)$" to the listdic 
    and verifies again until there's no match.
        Args:
        farm_name_list (str): The name to check
        listdic (list): List of existing names to compare against
    
        Returns:
        str: A unique name that doesn't conflict with existing names""" 

        # Create a copy of the original name for suffixing
        base_name = listdic
        
        # Check if this exact name already exists in listdic
        if listdic not in farm_name_list:
            return listdic
        
        # If it does exist, we need to find an unique name by adding suffixes
        counter = 1
        while True:
            # Create new name with suffix pattern " - (\d+)$"
            new_name = f"{base_name} - {counter}"
            
            # Check if this new name exists in listdic
            if new_name not in farm_name_list:
                return new_name

            counter += 1

def creat_list(driver, wait, listdic, village_picked, farm_name_list):
    # Creates a list in case there is no list in the farmlist. 
    
    # Verifies if listdic possibility to be added
    if farm_name_list is not None:
        listdic = list_control(listdic, farm_name_list)

    print(f"Creating a 1st list for {listdic}...")
    
    #Click the button to creat a new list
    creat_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="stickyWrapper"]/button[1]')))
    creat_button.click()

    #Give a Name to the list
    list_name = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="createFarmListForm"]/label[1]/input')))
    list_name.clear()
    list_name.send_keys(listdic)

    #Select village from the user: village_picked
    options = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="createFarmListForm"]/label[2]/select/option')))
    for option in options:
        if option.text.strip() == village_picked:
            # Select the option by clicking it
            wait.until(EC.element_to_be_clickable(option)).click()
            break
    else:
        print("No village found to select in list creation")
    
    #Add Trops
    x_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="createFarmListForm"]/div[2]/label[1]/input')))
    x_input.clear()
    x_input.send_keys("5")
    
    #Click the key creat list
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="createFarmListForm"]/div[4]/button[2]'))).click()
    time.sleep(10)


    dropContainer = find_list(driver, wait, listdic, village_picked)
    return dropContainer

def find_list(driver, wait, listdic, village_picked):
    """ Funtion that reads the dropcontainer of the pointed village and checks the already saved in villageWrapper if so check if the chosen list, (listdic) is in,
    so could then check the number of vilages inside"""
    try:
        colapse(driver, wait)
        # Open the farm list page and detect the right section with the id "rallyPointFarmList".
        rally_pointfarmlist = wait.until(EC.presence_of_element_located((By.ID, "rallyPointFarmList")))
        
        # Get all village wrappers inside the farm list
        village_wrappers = rally_pointfarmlist.find_elements(By.CLASS_NAME, "villageWrapper")

        for villagewarpper in village_wrappers:
            village_name = villagewarpper.find_element(By.CLASS_NAME, "villageName").text
            # If the village name matches the one picked by the user, proceed to check the farm list already saved by the user.
            if village_name == village_picked:
                # Get the name of the farm inside each dropContainer.
                for dropContainer in villagewarpper.find_elements(By.CLASS_NAME, "dropContainer"):
                    farm_name_list = dropContainer.find_element(By.CLASS_NAME, "name")
                    # If the 8 begging letters of the farm_name_list match with the names in the list_names.jon file.
                    farm_name_list = farm_name_list.text.strip()
                    if listdic == farm_name_list[:len(listdic)]:
                            max_village = dropContainer.find_element(By.CLASS_NAME, "farmListStatus")
                            # If the number of village is 100. Then it will click on
                            numbers = re.findall(r"\d+", max_village.text)
                            first_value = int(numbers[1])
                            if first_value == 100:
                                # Creat a new list because the list is already full
                                dropContainer = creat_list(driver, wait, listdic, village_picked, farm_name_list)
                                return dropContainer
                            else:
                                 ## Input_cords
                                return dropContainer
                print("No farm list to the vilage pikedup")
                farm_name_list = None
                dropContainer = creat_list(driver, wait, listdic, village_picked, farm_name_list)
                return dropContainer
                    
        print("The picked village has not yet any farm list")
        farm_name_list = None
        dropContainer = creat_list(driver, wait, listdic, village_picked, farm_name_list)
        return dropContainer

            
    except Exception as e:
        print(f"An error occurred while cleaning data: {e}")
    return None

def input_cords(driver, wait, cord_x, cord_y, dropContainer):
    """Input the coordinates in the respective fields and click the button to refresh the page with the coordinates"""
    
    colapse(driver, wait)
    # Expand the list to add the village to the correct list
    time.sleep(3)
    expand_collapse = dropContainer.find_element(By.CLASS_NAME, "expandCollapse")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", expand_collapse)
    expanded = wait.until(EC.element_to_be_clickable(expand_collapse))
    expanded.click()
    time.sleep(2)

    # Click over the button "add target" of the respective list
    add_twon = dropContainer.find_element(By.CLASS_NAME, "addTarget")
    add_twon = wait.until(EC.element_to_be_clickable((add_twon)))
    # Scroll in case the button is out of the screen
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_twon)
    time.sleep(1)

    add_twon.click()
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
        #print(f"   ✓ Village ({cord_x}|{cord_y}) successfully added to the farmlist.")
        pass

def save(df_inact, cord_x, cord_y):
    """Save the progress of the update of farm list"""
    # Turn the not processed (True) into a False processed
    df_inact.loc[(df_inact['X'] == int(cord_x)) & (df_inact['Y'] == int(cord_y)), 'ProgressFarm'] = False
    df_inact.to_csv('data/farm_progress.csv', index=False)

def scan_villages_list(wait, driver, village_picked):
    """This function will scan all the villages in the game and return a dataframe of villages that are already processed. """

    # Open list_names.json file to get the list_names.
    if os.path.exists(FILE):
        with open(FILE) as f:
            list_names = list(json.load(f))

    # Initialize empty DataFrame or load existing data
    df_saved_vilages = pd.DataFrame(columns=["Farm Name", "Target"])

    # Disponible list in the apointed city
    diponible_list = []

    # Check the expanded containers
    colapse(driver, wait)

    try:
        # Open the farm list page and detect the right section with the id "rallyPointFarmList".
        rally_pointfarmlist = wait.until(EC.presence_of_element_located((By.ID, "rallyPointFarmList")))
        
        # Get all village wrappers inside the farm list
        village_wrappers = rally_pointfarmlist.find_elements(By.CLASS_NAME, "villageWrapper")

        for villagewarpper in village_wrappers:
            village_name = villagewarpper.find_element(By.CLASS_NAME, "villageName").text
            # If the village name matches the one picked by the user, proceed to check the farm list already saved by the user.
            if village_name == village_picked:
                # Get the name of the farm inside each dropContainer.
                for dropContainer in villagewarpper.find_elements(By.CLASS_NAME, "dropContainer"):
                    farm_name_list = dropContainer.find_element(By.CLASS_NAME, "name")
                    # If the 8 begging letters of the farm_name_list match with the names in the list_names.jon file.
                    farm_name_list = farm_name_list.text.strip()
                    if any(name[:8] == farm_name_list[:8] for name in list_names):
                        # Must expand the container first before checking the targets.
                        expand_collapse = dropContainer.find_element(By.CLASS_NAME, "expandCollapse")
                        expanded = wait.until(EC.element_to_be_clickable(expand_collapse))
                        expanded.click()
                        # Quick pause to open correctly the container.
                        time.sleep(2)
                        
                        # Start to check the targets associed with that farm name in the farmListWrapper after expanded, and save it in a dataframe.
                        farmListWrapper_expanded = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".farmListWrapper.expanded")))
                        targets = farmListWrapper_expanded.find_elements(By.CSS_SELECTOR,"td.target a span")

                        for target in targets:
                            target = target.text.strip()
                            df = pd.DataFrame({"Farm Name": [farm_name_list], "Target": [target]})
                            df_saved_vilages = pd.concat([df_saved_vilages, df], ignore_index=True)
                        # Need to collapse the container to open a new one to scan it again. The button is the same as expand.
                        collapse = expanded
                        collapse.click()

                        # Quick pause to close correctly the container.
                        time.sleep(2)

                        # Add Farm_name_list to a diponible_list
                        if farm_name_list:
                            diponible_list.append(farm_name_list)

                        print(f"One list scaned {farm_name_list}")
                    else:
                        if farm_name_list:
                            print(f"The {farm_name_list} is not in the standard list names.")
                        else:
                            print("No farms list match with the standard format.")
                # Save df into a csv
                df_saved_vilages.to_csv("data/saved_vilages.csv", index=False)

                print(df_saved_vilages)
                return df_saved_vilages
            else:
                continue
        print(f"No saved list found to the picked village {village_picked} the game.")
        return None


    except Exception as e:
        print(f"An error occurred while scraping the farm list: {e}")

def clean_data(df_inact, df_saved_vilages):
    """This function will delete the villages from df_inact that existe in df_saved_vilages"""
    try:
        # Convert target column to string for proper comparison
        # Check if Target column exists and DataFrame is not empty
        if df_saved_vilages is not None:
            df_inact['Village'] = df_inact['Village'].astype(str)
            df_saved_vilages['Target'] = df_saved_vilages['Target'].astype(str)

            # Filter out rows in df_inact where Village exists in df_saved_vilages['Target']
            df_inact_cleaned = df_inact[~df_inact['Village'].isin(df_saved_vilages['Target'])]
            return df_inact_cleaned
        else:
            # Return original if no comparison can be made
            return df_inact

    except Exception as e:
        print(f"An error occurred while cleaning data: {e}")
        return None


def farmlist(driver, wait, df_inact, server_picked, village_picked):
    """Open the farmlist page and add the villages from the dataframe to the respective lists based on their population"""
    server = {"EUROPA 10": "ts10.x1.europe", "INTERNATIONAL 4": "ts4.x1.international"}
    print("Opening Farmlist...")
    driver.get(f"https://{server[server_picked]}.travian.com/build.php?id=39&gid=16&tt=99")
    print("   ✓ Farmlist opened, starting to add targets...")
    time.sleep(2)

    # Get the village already in farm list
    df_saved_vilages = scan_villages_list(wait, driver,village_picked)
    # Delete the villages from scrap that already are in farm list
    df_inact = clean_data(df_inact, df_saved_vilages)

    for x in tqdm(range(len(df_inact))):
        # Load the list of names for the farmlist categories from a json file
        if os.path.exists(FILE):
            with open(FILE) as f:
                listdic = list(json.load(f))

        # Get the coordinates of the village from the dataframe       
        cord_x = df_inact.iloc[x]['X']
        cord_y = df_inact.iloc[x]['Y']

        # Check the expanded containers
        colapse(driver, wait)

        if df_inact.iloc[x]['Player'] == 'Natars':
             if df_inact.iloc[x]['População'] > 150:
                print(f"   ✓ Village in ({cord_x}|{cord_y}) with population {df_inact.iloc[x]['População']} classified as a Natars 150 Plus.")
                dropContainer = find_list(driver, wait, listdic[4], village_picked)
                input_cords(driver, wait, cord_x, cord_y, dropContainer)
                print(f"   ✓ Village in ({cord_x}|{cord_y}) added to the farmlist Natars 150 Plus.")
                save(df_inact, cord_x, cord_y)

             else:
                print(f"   ✓ Village in ({cord_x}|{cord_y}) with population {df_inact.iloc[x]['População']} classified as a Natars 0 - 150.")
                dropContainer = find_list(driver, wait, listdic[5], village_picked)
                input_cords(driver, wait, cord_x, cord_y, dropContainer)
                print(f"   ✓ Village in ({cord_x}|{cord_y}) added to the farmlist Natars 0 - 150.")
                save(df_inact, cord_x, cord_y)
        else:                  
            if df_inact.iloc[x]['População'] > 250:
                print(f"   ✓ Village in ({cord_x}|{cord_y}) with population {df_inact.iloc[x]['População']} classified as a Pop 250 Plus.")
                dropContainer = find_list(driver, wait, listdic[0], village_picked)
                input_cords(driver, wait, cord_x, cord_y, dropContainer)
                print(f"   ✓ Village in ({cord_x}|{cord_y}) added to the farmlist Pop 250 Plus.")
                save(df_inact, cord_x, cord_y)
            
            elif df_inact.iloc[x]['População'] >= 100 and df_inact.iloc[x]['População'] <= 250:
                print(f"   ✓ Village in ({cord_x}|{cord_y}) with population {df_inact.iloc[x]['População']} classified as a Pop 100 - 250.")
                dropContainer = find_list(driver, wait, listdic[1], village_picked)
                input_cords(driver, wait, cord_x, cord_y, dropContainer)
                print(f"   ✓ Village in ({cord_x}|{cord_y}) added to the farmlist Pop 100 - 250.")
                save(df_inact, cord_x, cord_y)        
            
            elif df_inact.iloc[x]['População'] >= 50 and df_inact.iloc[x]['População'] < 100:
                print(f"   ✓ Village in ({cord_x}|{cord_y}) with population {df_inact.iloc[x]['População']} classified as a Pop 50 - 100.")
                dropContainer = find_list(driver, wait, listdic[2], village_picked)
                input_cords(driver, wait, cord_x, cord_y, dropContainer)
                print(f"   ✓ Village in ({cord_x}|{cord_y}) added to the farmlist Pop 50 - 100.")
                save(df_inact, cord_x, cord_y)        
            
            elif df_inact.iloc[x]['População'] > 0 and df_inact.iloc[x]['População'] < 50:
                print(f"   ✓ Village in ({cord_x}|{cord_y}) with population {df_inact.iloc[x]['População']} classified as a Pop 0 - 49.")
                dropContainer = find_list(driver, wait, listdic[3], village_picked)
                input_cords(driver, wait, cord_x, cord_y, dropContainer)
                print(f"   ✓ Village in ({cord_x}|{cord_y}) added to the farmlist Pop 0 - 49.")
                save(df_inact, cord_x, cord_y)
    
    return print("## Farmlist updated successfully! ##")
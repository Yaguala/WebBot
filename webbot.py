# WebBot 1.0 - A tool for automating tasks in the Travian game.
# Developed by Pedro Andrade - 2026
# This script allows you to log in, scrape inactive villages, and send attacks based on available troops.

# Importing necessary libraries
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
import time
import pandas as pd
from tqdm import tqdm
import os
import pyautogui

# Importing functions from other modules
from modules.farmlist import farmlist
from modules.login import fazer_login
from modules.ataque import scrap_tropas, lancamento
from modules.scraper import scrap_vilas_bs4
from modules.pickvillage import village_chose, click_village
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Setting up Selenium WebDriver with Chrome
options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Fullscreen mode
options.add_argument("--start-fullscreen")

# Disable the "controlled by automation" indicator
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# Unable passowrd to be saved in Chrome browser
#options.add_argument("--disable-password-saving")
#options.add_argument("--disable-autofill")
options.add_experimental_option("prefs", {"credentials_enable_service": False,"profile.password_manager_enabled": False})

# Option to access email and password information of the user
def get_user_credentials():

    # Import necessary modules from the auth_utils module
    from credentials.auth_utils import load_credentials, save_credentials

    # Check if credentials are already saved using new utility
    credentials = load_credentials()

    if credentials:
        return credentials['email'], credentials['password']
    else:
        print("No saved credentials found. Please enter your email and password.")

        # Get user input for email and password
        email = input("Enter your email: ")
        password = input("Enter your password: ")
        
        # Save the credentials
        save_credentials(email, password)

        # Return the newly saved credentials
        credentials = load_credentials()
        return credentials['email'], credentials['password']


# Vilages to scrape and Found.
def players_vilages(wait):
    print("Getting the list of villages...")
    print("From the list of villages, please choose the village you want to use for scraping or sending attacks.")
    try:
        # Get the server names in the section class yourGameworlds.
        village_section = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "villageList "))
        )

        # Find all server names and print them with their corresponding numbers
        for village_name in village_section.find_elements(By.CLASS_NAME, "dropContainer"):
            village = village_name.find_element(By.XPATH, ".//a/div/span[2]")
            countserver = village_section.find_elements(By.CLASS_NAME, "dropContainer").index(village_name) + 1
            print(f"   Found    Village {countserver} : {village.text}")

        # Get the user input for the server number position.
        x = int(input("   Enter the number corresponding to the village you want as selector point (1, 2, 3, ...): "))
        
        # Click the Play button for the selected server X
        village_coord_X = wait.until(
            EC.presence_of_element_located((By.XPATH, f'//*[@id="sidebarBoxVillageList"]/div[2]/div[2]/div[{x+1}]/div/span/span/span[1]'))
        ).text[1:]
        vilage_coord_Y = wait.until(
            EC.presence_of_element_located((By.XPATH, f'//*[@id="sidebarBoxVillageList"]/div[2]/div[2]/div[{x+1}]/div/span/span/span[3]'))
        ).text[:-1]

        village_name = village_section.find_elements(By.CLASS_NAME, 'dropContainer')[x-1]
        village_picked = village_name.find_element(By.XPATH, ".//a/div/span[2]").text

        print(f"Village chosen: {village_picked} with coordinates: {village_coord_X} : {vilage_coord_Y} ")
    except Exception as e:
        print(f"Error finding server section: {e}")
        
    return village_coord_X, vilage_coord_Y, village_picked

print("WebBot 1.0 Started!\nDeveloped by Pedro Andrade - 2026")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 20)

# Return to the previous application (e.g. VS Code)
time.sleep(1)
pyautogui.hotkey("command", "tab")
pyautogui.hotkey("alt", "tab")

try:
    # Executa o fluxo completo
    EMAIL, PASSWORD = get_user_credentials()
    server_picked, sucesso_login = fazer_login(driver, wait, EMAIL, PASSWORD)

    if sucesso_login:
        print("Loggin successful! What do you want to do?")
        print("1 - Update farmlist")
        print("2 - Send attacks")
        x = input()
        if x == "1":
            # Check if there is a old session to be continued
            # Import the progress of the farm list if there is a session in progress.
            os.path.exists('data/farm_progress.csv')
            df_farm_progress = pd.read_csv('data/farm_progress.csv')
            if df_farm_progress is not None and df_farm_progress["ProgressFarm"].any():
                keep_progress = ""
                while keep_progress != "Y" and keep_progress != "n":
                    print("There are still a old session. Do you want to continue Session? Y/n")
                    keep_progress = input()
                    if keep_progress == "Y":
                        # Select only the ones not processed
                        df_inact = df_farm_progress[df_farm_progress['ProgressFarm'] == True]
                        village_coord_X, vilage_coord_Y, village_picked = players_vilages(wait)
                        farmlist(driver, wait, df_inact, server_picked, village_picked)
                        break
                    elif keep_progress == "n":
                        # Normal session with delete the progress of the attacks and start a new one.
                        print("- Starting a New Session will delete the progress of old session. Do you want to continue? Y/n")
                        if input() == "Y":
                            # Update farmlist
                            village_coord_X, vilage_coord_Y, village_picked = players_vilages(wait)
                            villages_to_scrape = int(input("How many villages do you want to add to the farmlist?"))
                            print(f"Starting scrape for {villages_to_scrape} villages ...")
                            df_inact = scrap_vilas_bs4(server_picked, villages_to_scrape, village_coord_X, vilage_coord_Y)
                            df_inact['ProgressFarm'] = True
                            print("\n Scraping inactive villages!")
                            print(df_inact)
                            df_inact.to_csv('data/farm_progress.csv', index=False)
                            farmlist(driver, wait, df_inact, server_picked, village_picked)
                            break
                        else:
                            print("- Exiting the program...")
            else:
                # Update farmlist
                village_coord_X, vilage_coord_Y, village_picked = players_vilages(wait)
                villages_to_scrape = int(input("How many villages do you want to add to the farmlist?"))
                print(f"Starting scrape for {villages_to_scrape} villages ...")
                df_inact = scrap_vilas_bs4(server_picked, villages_to_scrape, village_coord_X, vilage_coord_Y)
                df_inact['ProgressFarm'] = True
                print("\n Scraping inactive villages!")
                print(df_inact)
                df_inact.to_csv('data/farm_progress.csv', index=False)
                farmlist(driver, wait, df_inact, server_picked, village_picked)

        elif x == "2":
            # Import the progress of the attacks if there is a session in progress.
            os.path.exists('data/inact_progress.csv')
            df_inact_progress = pd.read_csv('data/inact_progress.csv')
            if df_inact_progress is not None and df_inact_progress["Progress"].any():
                keep_progress = ""
                while keep_progress != "Y" and keep_progress != "n":
                    print("There are still attacks to be sent. Do you want to continue Session? Y/n")
                    keep_progress = input()
                    if keep_progress == "Y":
                        # Get the village that is making the atack
                        village_number = df_inact_progress['Village_atacker'].iloc[0]
                        click_village(wait, village_number)

                        # Get Non atacks made
                        df_inact = df_inact_progress[df_inact_progress['Progress'] == True]
                        
                        # Launch do attacks
                        ataque_confirmado, sem_aldeia = lancamento(driver, wait, df_inact)
                        break
                    elif keep_progress == "n":
                        # Normal session with delete the progress of the attacks and start a new one.
                        print("- Starting a New Session will delete the progress of the attacks. Do you want to continue? Y/n")
                        if input() == "Y":
                            village_coord_X, vilage_coord_Y, village_picked = players_vilages(wait)
                            villages_to_scrape = int(input("You wish to make how many attacks?  "))
                            print(f"Looking for {villages_to_scrape} Villages to attack...")
                            df_inact = scrap_vilas_bs4(server_picked, villages_to_scrape, village_coord_X, vilage_coord_Y)

                            # Add a Progress column to the dataframe to keep track of which attacks have been sent
                            df_inact['Progress'] = True
                            ataque_confirmado, sem_aldeia = lancamento(driver, wait, df_inact)
                            break
                        else:
                            print("- Exiting the program...")
                        exit()
                    else:
                        print("- Please choose a valid option.")
                        exit()
            else:
                print("- No previous session found. Starting a new session...")
                server = {"EUROPA 10": "ts10.x1.europe", "INTERNATIONAL 4": "ts4.x1.international"}

                driver.get(f"https://{server[server_picked]}.travian.com/build.php?id=39&gid=16&tt=2")        
                
                # Ckeck number of villages, and trops in each
                df_village_table = village_chose(wait, driver)
                
                for row in df_village_table.itertuples():
                    print(f"Village number: [{row.Village_number}] \nVillage Name: {row.Village_Name}")
                    print("------------------------------------------------")
                    village_number = row.Village_number
                    click_village(wait, village_number)
                    SALTEADORES, PALADINO = scrap_tropas(driver, wait)
                    print(f"Current troops available: {SALTEADORES} Salteadores and {PALADINO} Paladinos.")
                    max_ataques_salteadores = SALTEADORES // 5 + PALADINO // 2
                    print(f"You have the following troops available:\n {SALTEADORES} Salteadores\n {PALADINO} Paladinos.")
                    print(f"You can send a max of attacks: {max_ataques_salteadores} .\n {SALTEADORES // 5} with Salteadores \n {PALADINO // 2} with Paladinos.\n\n")
                
                # Click to chose the village in case there is more then one.
                if village_number >= 2:
                    village_number = int(input("Chose the Number of Village you wish to start atack with. "))
                    click_village(wait, village_number)

                # Check for how many ataques whish to make
                village_coord_X, vilage_coord_Y, village_picked = players_vilages(wait)
                villages_to_scrape = int(input("You wish to make how many attacks?  "))
                print(f"Looking for {villages_to_scrape} Villages to attack...")
                df_inact = scrap_vilas_bs4(server_picked, villages_to_scrape, village_coord_X, vilage_coord_Y)

                # Add a Progress column to the dataframe to keep track of which attacks have been sent, and the village that is atacking.
                df_inact['Village_atacker'] = village_number
                df_inact['Progress'] = False
                ataque_confirmado, sem_aldeia = lancamento(driver, wait, df_inact)

            print(f"\nExecutado com sucesso! ataques confirmados: {ataque_confirmado}, sem aldeia: {sem_aldeia}")
            os.remove('data/inact_progress.csv')
        else:
            print("Opção inválida. Encerrando o programa.")
    else:
        print("## Falha no login. Verifique suas credenciais e tente novamente. ##")

except Exception as e:
    print(f"\n ## ERRO GERAL: {e}")

finally:
    input("\n ## Pressiona ENTER para fechar o navegador... ##")
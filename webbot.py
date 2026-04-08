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

# Importing functions from other modules
from modules.config import EMAIL, PASSWORD
from modules.farmlist import farmlist
from modules.login import fazer_login
from modules.ataque import scrap_tropas, lancamento
from modules.scraper import scrap_vilas_bs4
from modules.pickvillage import village_chose, click_village

# Setting up Selenium WebDriver with Chrome
options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
# options.add_argument("--headless")



print("WebBot 1.0 Started!\nDeveloped by Pedro Andrade - 2026")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 20)

try:
    # Executa o fluxo completo
    sucesso_login = fazer_login(driver, wait, EMAIL, PASSWORD)

    if sucesso_login:
        print("Loggin successful! What do you want to do?")
        print("1 - Update farmlist")
        print("2 - Send attacks")
        x = input()
        if x == "1":
            # Update farmlist
            villages_to_scrape = int(input("How many villages do you want to add to the farmlist?"))
            print(f"Starting scrape for {villages_to_scrape} villages ...")
            df_inact = scrap_vilas_bs4(villages_to_scrape)
            print("\n Scraping inactive villages!")
            print(df_inact)
            farmlist(driver, wait, df_inact)

        elif x == "2":
            # Import the progress of the attacks if there is a session in progress.
            if os.path.exists('data/inact_progress.csv'):
                df_inact_progress = pd.read_csv('data/inact_progress.csv')
                keep_progress = ""
                while keep_progress != "Y" and keep_progress != "n":
                    print("There are still attacks to be sent. Do you want to continue Session? Y/n")
                    keep_progress = input()
                    if keep_progress == "Y":
                        # Get the village that is making the atack
                        village_number = df_inact_progress['Village_atacker'].iloc[0]
                        click_village(wait, village_number)

                        # Get Non atacks made
                        df_inact = df_inact_progress[df_inact_progress['Progress'] == False]
                        
                        # Launch do attacks
                        ataque_confirmado, sem_aldeia = lancamento(driver, wait, df_inact)
                        break
                    elif keep_progress == "n":
                        # Normal session with delete the progress of the attacks and start a new one.
                        print("- Starting a New Session will delete the progress of the attacks. Do you want to continue? Y/n")
                        if input() == "Y":
                            villages_to_scrape = int(input("You wish to make how many attacks?  "))
                            print(f"Looking for {villages_to_scrape} Villages to attack...")
                            df_inact = scrap_vilas_bs4(villages_to_scrape)
                            
                            # Add a Progress column to the dataframe to keep track of which attacks have been sent
                            df_inact['Progress'] = False
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

                driver.get("https://ts10.x1.europe.travian.com/build.php?id=39&gid=16&tt=2")        
                
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
                villages_to_scrape = int(input("You wish to make how many attacks?  "))
                print(f"Looking for {villages_to_scrape} Villages to attack...")
                df_inact = scrap_vilas_bs4(villages_to_scrape)
                
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
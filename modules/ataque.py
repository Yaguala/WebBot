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

# Pick the right number of trops
def lancamento(driver, wait, df_inact):
    """Launch the attack with the specified troops to the specified coordinates, 
    \nand return the updated count of confirmed attacks and attacks that failed due to no village at the coordinates."""
    
    ataque_confirmado, sem_aldeia = 0, 0
    num_ataques = len(df_inact)
    for x in tqdm(range(num_ataques)):

        driver.get("https://ts10.x1.europe.travian.com/build.php?id=39&gid=16&tt=2")
        
        TARGET_X = str(df_inact.iloc[x]['X'])
        TARGET_Y = str(df_inact.iloc[x]['Y'])
        SALTEADORES, PALADINO = scrap_tropas(driver, wait)
        print("\nAvailable Troops")
        print(f"   - ROBBERS: {SALTEADORES}")
        print(f"   - PALADINO: {PALADINO}")
        if SALTEADORES >= 5:
            quantidade_salteadores = "5"  # valor padrão
            quantidade_paladinos = None  # valor padrão
            ataque_confirm, ataque_confirmado, sem_aldeia = enviar_ataque(driver, wait, TARGET_X, TARGET_Y, quantidade_salteadores, quantidade_paladinos, ataque_confirmado, sem_aldeia)
            if ataque_confirm == True:
                df_inact.loc[(df_inact['X'] == int(TARGET_X)) & (df_inact['Y'] == int(TARGET_Y)), 'Progress'] = True
                df_inact.to_csv('data/inact_progress.csv', index=False)
        elif SALTEADORES < 5 and PALADINO >= 2:
            quantidade_paladinos = "2"
            quantidade_salteadores = None
            ataque_confirm, ataque_confirmado, sem_aldeia = enviar_ataque(driver, wait, TARGET_X, TARGET_Y, quantidade_salteadores, quantidade_paladinos, ataque_confirmado, sem_aldeia)
            if ataque_confirm == True:
                df_inact.loc[(df_inact['X'] == int(TARGET_X)) & (df_inact['Y'] == int(TARGET_Y)), 'Progress'] = True
                df_inact.to_csv('data/inact_progress.csv', index=False)
        else:
            print(f"## Not enought trops to make the atack {TARGET_X}|{TARGET_Y} (Salteadores: {SALTEADORES}, Paladinos: {PALADINO}) \nAttacks ended number of attacks : {x}.")
            break
        continue
    return ataque_confirmado, sem_aldeia


# Scraping of available troops
def scrap_tropas(driver, wait):
        """Check available troops"""

        SALTEADORES = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="troops"]/tbody/tr[1]/td[1]/a | //*[@id="troops"]/tbody/tr[1]/td[1]/span'))
        ).text.strip()
        SALTEADORES = int(re.sub(r'\D', '', SALTEADORES))

        PALADINO = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="troops"]/tbody/tr[2]/td[2]/a | //*[@id="troops"]/tbody/tr[2]/td[2]/span'))
        ).text.strip()
        PALADINO = int(re.sub(r'\D', '', PALADINO))

        
        return SALTEADORES, PALADINO




# Send the Attack
def enviar_ataque(driver, wait, x_coord, y_coord, quantidade_salteadores, quantidade_paladinos, ataque_confirmado, sem_aldeia):
    """Send the attack with the specified troops to the specified coordinates, 
    \nand return the updated count of confirmed attacks and attacks that failed due to no village at the coordinates."""

    print("Preparing to send attack...")
    time.sleep(2)

    # Coordinate input
    x_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="xCoordInput"]')))
    x_input.clear()
    x_input.send_keys(x_coord)

    y_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="yCoordInput"]')))
    y_input.clear()
    y_input.send_keys(y_coord)

    # Salteadores
    if quantidade_salteadores is not None:       
        salteadores_input = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="troops"]/tbody/tr[1]/td[1]/input'))
        )
        salteadores_input.clear()
        salteadores_input.send_keys(quantidade_salteadores)
        print(f"   - Adding  {quantidade_salteadores} Salteadores")

    # Paladinos
    if quantidade_paladinos is not None:
        paladino_input = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="troops"]/tbody/tr[2]/td[2]/input'))
        )
        paladino_input.clear()
        paladino_input.send_keys(quantidade_paladinos)
        print(f"   - Adding {quantidade_paladinos} Paladinos")

    # Selection type of attack
    attack_type = wait.until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="build"]/div/form/div[2]/label[3]/input'))
    )
    attack_type.click()

    # Click button send
    send_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ok"]')))
    send_btn.click()

    # Check for error messages related to coordinates and handle them if they appear, counting them in the variable sem_aldeia if they do
    try:
        erro = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="build"]/div/p'))
        )

        if erro.text is not None:
            print(f"⚠️ Não há aldeia em ({x_coord}|{y_coord}). Ataque cancelado.")
            sem_aldeia +=1
            return ataque_confirmado, sem_aldeia

    except TimeoutException:
        # If no error appears keep going with the process
        pass

    # Confirm the attack
    confirm_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="confirmSendTroops"]')))
    confirm_btn.click()
    ataque_confirmado +=1
    ataque_confirm = True
    print(f"   - Attack confirmed and sent to ({x_coord}|{y_coord})")
    print("\n")

    return ataque_confirm, ataque_confirmado, sem_aldeia
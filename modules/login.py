# login.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def fazer_login(driver, wait, email, password):
    """Log in to Travian and join the Europa 10 server."""
    
    print("1. Opening the main page")
    driver.get("https://www.travian.com")

    # Click on the Login button
    login_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Login') or contains(@class, 'Login')]"))
    )
    login_btn.click()
    print("2. Login button clicked")

    time.sleep(2)

    # Fill in the login form
    print("4. Filling in credentials...")
    email_input = wait.until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="loginLobby"]/form//input[@name="name"]'))
    )
    email_input.clear()
    email_input.send_keys(email)

    password_input = wait.until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="loginLobby"]/form//input[@name="password"]'))
    )
    password_input.clear()
    password_input.send_keys(password)

    # Submit the login form
    submit_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="loginLobby"]//button[@type="submit" or contains(., "Login")]'))
    )
    submit_btn.click()
    print("5. Login submitted!")

    time.sleep(3)
    driver.switch_to.default_content()

    # Clicar no Play Now
    print("6. Selecting server (Play Now)...")
    time.sleep(3)

    play_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="accountAvatars"]/section[1]/div[1]/div[2]/button'))
    )
    play_button.click()
    print("7. Entering the Europa 10 server...")

    time.sleep(3)
    print("## Login and entry into the server completed successfully! ##\n")

    return True
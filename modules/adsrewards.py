from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from tqdm import tqdm

# Load the web page to see the videos that will reward extra  production of resources in the game


def advantagesBonusBox(wait, productionBonus):
    """Function to click on the production bonus button"""
    time.sleep(3)
    try:
        # First check if element exists before trying to interact with it
        element = productionBonus.find_element(By.CSS_SELECTOR, ".textButtonV2.buttonFramed.withTextAndIcon.rectangle.withText.purple")
        if element:
            productionBonus_button = wait.until(EC.element_to_be_clickable(element))
            productionBonus_button.click()
            return True
    except Exception:
        print("Production bonus button not found - continuing execution")
        return False

def watchVideo(wait):
    """Function to click on the watch video button in the new dialcontent"""
    time.sleep(3)
    try:
        # First check if element exists before trying to interact with it
        watch_video = wait.until(EC.presence_of_element_located((By.ID, "videoFeature")))
        if watch_video:    
            element = watch_video.find_element(By.CSS_SELECTOR, ".textButtonV2.buttonFramed.withTextAndIcon.rectangle.withText.purple")
            watch_video_button = wait.until(EC.element_to_be_clickable(element))
            watch_video_button.click()
            time.sleep(2)
    except Exception:
        print("Watch video button not found - continuing execution")
        pass

def playvideo(driver, wait):
    """Function to click on the play video button in the new dialcontent"""
    print("Play the video")
    time.sleep(3)
    try:
        # Must Switch off iframe to play video
        videoArea = wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "videoArea")))
        if videoArea:
            time.sleep(3)
            element = driver.find_element(By.CSS_SELECTOR, ".atg-gima-big-play-button-outer")
            play_video_button = wait.until(EC.element_to_be_clickable(element))
            play_video_button.click()
            for _ in tqdm(range(40), desc="Playing", unit="sec", leave=True):
                time.sleep(1)
    except Exception :
        # Button not found, continue execution without error    
        print("Play video button not found - continuing execution")
        for _ in tqdm(range(40), desc="Waiting", unit="sec", leave=True):
            time.sleep(1)
    finally:
        # After the video get back to iframe default
        driver.switch_to.default_content()
    pass

def adsrewards(driver, wait):
    print("Starting the videos adds to get bonus resources rewards")
    topbar = wait.until(EC.presence_of_element_located((By.ID, "header")))
    shop = topbar.find_element(By.CLASS_NAME, "shop")
    shopbutton = wait.until(EC.element_to_be_clickable(shop))
    shopbutton.click()
    time.sleep(2)

    # Click button in shopbox Advantages
    shop_conotainer = wait.until(EC.presence_of_element_located((By.ID, "paymentWizard")))
    scrollingContainer = shop_conotainer.find_element(By.CLASS_NAME, "scrollingContainer")
    advantage_button = scrollingContainer.find_elements(By.CSS_SELECTOR, ".content.favor")
    advantage_button = wait.until(EC.element_to_be_clickable(advantage_button[3]))
    advantage_button.click()
    time.sleep(2)

    # Click in the diferents 4 prodution bonus buttons.
    paymentWizardContent = wait.until(EC.presence_of_element_located((By.ID, "paymentWizardContent")))

    bonusbox = {"lumber bonus": ".advantagesBonusBox.lumberProductionBonus",
                "clay bonus": ".advantagesBonusBox.clayProductionBonus",
                "iron  bonus": ".advantagesBonusBox.ironProductionBonus",
                "crop bonus": ".advantagesBonusBox.cropProductionBonus"}

    for key, value in bonusbox.items():
        productionBonus = paymentWizardContent.find_element(By.CSS_SELECTOR, value)
        print(f"Advantages bonus for {key}")
        #Click prodution bonus
        if advantagesBonusBox(wait, productionBonus):
            # Click in watch video in the new dialcontent
            watchVideo(wait)
            # Click the play video
            playvideo(driver, wait)

    return
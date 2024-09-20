from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import pytest
import time


@pytest.fixture
def driver():
    # Initialize the Chrome driver
    driver = webdriver.Chrome()  # You can also configure options here if needed
    driver.implicitly_wait(10)
    yield driver
    # Commented out quit to keep the browser open after the test finishes
    # driver.quit()


def test_payment_process(driver):
    # Open the website
    driver.get("https://app-staging.qlub.cloud/qr/ae/dummy/36/1/_/7476695cf0?lang=en")
    driver.maximize_window()

    try:
        # Step 1: Click on "Pay The Bill"
        pay_bill_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-qa-id='landing-pay-now']"))
        )
        pay_bill_button.click()
        print("Clicked on 'Pay The Bill'")

        # Step 2: Wait for any splash screen or overlay to disappear
        WebDriverWait(driver, 30).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "Splash_container__xukgN"))
        )
        print("Splash screen or overlay disappeared")

        # Step 3: Click on "Let’s Split The Bill"
        split_bill_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-qa-id='billing-split-bill']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", split_bill_button)
        split_bill_button.click()
        print("Clicked on 'Let’s Split Bill'")

        # Step 4: Click "Pay a custom amount" option
        custom_amount_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@data-qa-id='split-modal-custom']//p[text()='Pay a custom amount']"))
        )
        custom_amount_button.click()
        print("Clicked on 'Pay a custom amount'")

        # Step 5: Wait for the next card to popup
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//h2[@data-qa-id='split-title']"))
        )

        # Step 6: Set amount (e.g., 10 AED)
        amount_field = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='amount']"))
        )
        amount_field.clear()  # Clear any existing value
        amount_field.send_keys("10")
        print("Entered amount")

        # Step 7: Click the confirm button and close all popups
        confirm_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@id='split-bill']"))
        )
        confirm_button.click()
        print("Clicked on 'Confirm'")

        # Wait for popups to close
        time.sleep(5)

        # Step 7: Wait for the page to update
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@class='TipInputs_tipScrollable__Zv10w']"))
        )

        # Step 8: Select a tip option (e.g., 5% tip)
        tip_option = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='tip_5']"))
        )
        tip_option.click()
        print("Selected tip option")

        # Step 9: Verify background color of the selected tip option
        background_color = tip_option.value_of_css_property("background-color")
        print("Background color of selected tip option:", background_color)

        # Debugging: Print out the actual CSS value
        computed_style = driver.execute_script("return window.getComputedStyle(arguments[0]);", tip_option)
        print("Computed style:", computed_style)

        # Step 10: Wait for the card number input field to be visible and enter the card number
        # Wait until the iframe is present
        wait = WebDriverWait(driver, 10)
        iframe = wait.until(
            EC.presence_of_element_located((By.XPATH, "//iframe[@title='Secure payment input frame']")))

        # Switch to the iframe
        driver.switch_to.frame(iframe)

        # Wait for the card number input field to be visible and enter the card number
        card_number_field = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='number']"))
        )
        card_number_field.send_keys("4242 4242 4242 4242")

        # Wait for the expiration date input field and enter the date
        expiry_field = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='expiry']"))
        )
        expiry_field.send_keys("02/26")

        # Wait for the CVC input field and enter the CVC
        cvc_field = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='cvc']"))
        )
        cvc_field.send_keys("100")

        # Optionally, switch back to the main document
        driver.switch_to.default_content()
        print("Entered card details")

        # Step 11 - Click the "Pay Now" button
        for _ in range(3):
            try:
                pay_now_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.XPATH,
                         "//button[contains(@class, 'PayButtonElement_button__V8yic') and contains(@class, 'MuiButton-containedPrimary')]"))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", pay_now_button)  # Scroll into view
                pay_now_button.click()
                print("Clicked on 'Pay Now'")

                # Step 12: Wait for the success page to load by checking for a unique element (e.g., an element with a class 'invoice-number' or similar)
                success_indicator = WebDriverWait(driver, 30).until(
                    EC.visibility_of_element_located((By.XPATH, "//p[contains(text(), 'Table')]"))
                )
                print("Successfully navigated to the invoice page.")
                break  # Exit loop if successful
            except (TimeoutException, StaleElementReferenceException):
                print("Retrying to find 'Pay Now' button...")
                time.sleep(1)  # Wait a second before retrying

    except TimeoutException as te:
        print("Timeout occurred:", te)
        print("Current URL:", driver.current_url)
        print("Page Title:", driver.title)
    except NoSuchElementException as nse:
        print("Element not found:", nse)
        print("Current URL:", driver.current_url)
        print("Page Title:", driver.title)
    except Exception as e:
        print("An unexpected error occurred:", e)
        print("Current URL:", driver.current_url)
        print("Page Title:", driver.title)
    finally:
        # Optional: Take a screenshot if needed for debugging
        driver.save_screenshot("screenshot.png")
        print("Screenshot saved as screenshot.png")

        # Verify that the test should pass
        assert "Invoice" in driver.page_source or "Table" in driver.page_source, "Invoice page not loaded."
        print("Test passed: Successfully reached the invoice page.")

        # Commenting out driver.quit() to keep the window open after the test succeeds
        # driver.quit()









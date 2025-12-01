from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration ONLY from .env file (no hardcoded defaults)
CONFIG = {
    'email': os.getenv('EMAIL'),
    'full_name': os.getenv('FULL_NAME'),
    'address': os.getenv('ADDRESS'),
    'city': os.getenv('CITY'),
    'state': os.getenv('STATE'),
    'zip_code': os.getenv('ZIP_CODE'),
    'country': os.getenv('COUNTRY'),
    'phone': os.getenv('PHONE'),
    'card_number': os.getenv('CARD_NUMBER'),
    'card_expiry': os.getenv('CARD_EXPIRY'), 
    'card_cvc': os.getenv('CARD_CVC')
}

# Validate that all required variables are present
required_vars = ['EMAIL', 'FULL_NAME', 'ADDRESS', 'CITY', 'STATE', 'ZIP_CODE', 'CARD_NUMBER', 'CARD_EXPIRY', 'CARD_CVC']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    raise Exception(f"Missing required environment variables: {missing_vars}")

browser = webdriver.Firefox()
browser.get("https://p0nder.com/")
time.sleep(3)

try:
    wait = WebDriverWait(browser, 10)
    
    # Find the product card by the title
    product_title = wait.until(
        EC.presence_of_element_located((By.XPATH, "//h6[contains(text(), 'Spider T-Shirt Purple')]"))
    )
    print("✅ Product found after waiting!")
    print(f"Product text: {product_title.text}")
    
    # Find the product card container
    product_card = product_title.find_element(By.XPATH, "./ancestor::div[contains(@class, 'product')]")
    print("✅ Product card found")
    
    # Scroll into view first
    browser.execute_script("arguments[0].scrollIntoView(true);", product_card)
    time.sleep(1)
    
    # Hover over product to reveal overlay
    actions = ActionChains(browser)
    actions.move_to_element(product_card).perform()
    print("✅ Hover performed")
    time.sleep(2)
    
    try:
        # Try to Find the checkout button by its <a> and <div>
        checkout_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'btn-light') and .//div[text()='CHECKOUT']]"))
        )
        print("✅ Checkout button found!")
        checkout_button.click()
        print("✅ Checkout button clicked!")
        
    except Exception as e:
        print(f"❌ Could not find/click checkout button: {e}")
        print("💡 This is expected - proceeding to product detail page approach...")
        
        # Alternative: Try clicking the product link to go to detail page
        try:
            product_link = product_card.find_element(By.XPATH, ".//a[contains(@href, 'inStock-pages/stock3.html')]")
            print("✅ Found product detail link, clicking...")
            product_link.click()
            print("✅ Navigated to product detail page")
            
            # Wait for page to load and look for add to cart button
            time.sleep(3)
            
            try:
                stripe_link = wait.until(EC.element_to_be_clickable((By.ID, "purchaseBtn")))
                print("✅ Found checkout link via stripe, clicking...")
                stripe_link.click()
                print("✅ Navigated to stripe checkout page")
                time.sleep(3)
                
                # === STRIPE CHECKOUT FORM FILLING ===
                try:
                    print("🔄 Filling out checkout form...")
                    
                    # Wait for Stripe form to load completely
                    wait.until(EC.presence_of_element_located((By.ID, "email")))
                    time.sleep(2)
                    
                    # 1. Fill Email
                    email_field = wait.until(EC.element_to_be_clickable((By.ID, "email")))
                    email_field.clear()
                    email_field.send_keys(CONFIG['email'])
                    print("✅ Email filled")
                    
                    # 2. Fill Full Name (Contact Details)
                    name_field = wait.until(EC.element_to_be_clickable((By.ID, "individualName")))
                    name_field.clear()
                    name_field.send_keys(CONFIG['full_name'])
                    print("✅ Full name filled")
                    
                    # 3. Fill Shipping Name
                    shipping_name_field = wait.until(EC.element_to_be_clickable((By.ID, "shippingName")))
                    shipping_name_field.clear()
                    shipping_name_field.send_keys(CONFIG['full_name'])
                    print("✅ Shipping name filled")
                    
                    # 4. Select Country
                    country_dropdown = wait.until(EC.element_to_be_clickable((By.ID, "shippingCountry")))
                    select = Select(country_dropdown)
                    select.select_by_visible_text(CONFIG['country'])
                    print("✅ Country selected")
                    time.sleep(1)  # Wait for country selection to load state fields
                    
                    # 5. Fill Address
                    address_field = wait.until(EC.element_to_be_clickable((By.ID, "shippingAddressLine1")))
                    address_field.clear()
                    address_field.send_keys(CONFIG['address'])
                    print("✅ Address filled")
                    time.sleep(3)
                    address_field.send_keys(Keys.ENTER)
                    
                    # 6. Fill City (if visible) - sometimes hidden until country selected
                    try:
                        city_field = wait.until(EC.element_to_be_clickable((By.ID, "shippingLocality")))
                        city_field.clear()
                        city_field.send_keys(CONFIG['city'])
                        print("✅ City filled")
                    except:
                        print("ℹ️ City field not visible or not required")
                    
                    # 7. Select State (if visible)
                    try:
                        state_dropdown = wait.until(EC.element_to_be_clickable((By.ID, "shippingAdministrativeArea")))
                        select_state = Select(state_dropdown)
                        select_state.select_by_visible_text(CONFIG['state'])
                        print("✅ State selected")
                    except:
                        print("ℹ️ State field not visible or not required")
                    
                    # 8. Fill ZIP Code
                    try:
                        zip_field = wait.until(EC.element_to_be_clickable((By.ID, "shippingPostalCode")))
                        zip_field.clear()
                        zip_field.send_keys(CONFIG['zip_code'])
                        print("✅ ZIP code filled")
                    except:
                        print("ℹ️ ZIP field not visible or not required")

                    # 9. Fill Phone Number (if required)
                    try:
                        phone_field = wait.until(EC.element_to_be_clickable((By.ID, "phoneNumber")))
                        phone_field.clear()
                        phone_field.send_keys(CONFIG['phone'])
                        print("✅ Phone number filled")
                    except:
                        print("ℹ️ Phone field not visible or not required")
                    
                    # 10. Choose Payment Method - Click "Card" Option & Fill Out Card Info
                    try:
                        print("🔄 Checking payment method selection...")

                        card_radio = wait.until(EC.presence_of_element_located((By.ID, "payment-method-accordion-item-title-card")))
                        is_already_selected = browser.execute_script("return arguments[0].checked", card_radio)

                        if is_already_selected:
                            print("✅ Card payment is already selected by default")
                        else:
                            print("🔄 Selecting card payment method...")

                            # Select Card Payment 
                            try:
                                accordion_item = browser.find_element(By.CSS_SELECTOR, "[data-testid='card-accordion-item']")
                                actions = ActionChains(browser)
                                actions.move_to_element(accordion_item).click().perform()
                                print("✅ Clicked entire card accordion item as fallback")
                            except Exception as fallback_error:
                                print(f"❌ Ultimate fallback also failed: {fallback_error}")
                            print("✅ Card payment method selected")

                            # Verify
                            time.sleep(1)
                            is_checked = browser.execute_script("return arguments[0].checked", card_radio)
                            print(f"✅ Verified: {is_checked}")

                        # === NEW: FILL CARD INFORMATION HERE ===
                        print("🔄 Filling card information...")

                        # Wait for card form to be visible
                        time.sleep(2)

                        # 1. Fill Card Number
                        card_number_field = wait.until(EC.element_to_be_clickable((By.ID, "cardNumber")))
                        card_number_field.clear()
                        # Type slowly like a human
                        for char in CONFIG['card_number']:
                            card_number_field.send_keys(char)
                            time.sleep(0.05)
                        print("✅ Card number filled")
                        time.sleep(1)

                        # 2. Fill Expiration Date (MM / YY)
                        expiry_field = wait.until(EC.element_to_be_clickable((By.ID, "cardExpiry")))
                        expiry_field.clear()
                        for char in CONFIG['card_expiry']:
                            expiry_field.send_keys(char)
                            time.sleep(0.05)
                        print("✅ Expiry date filled")
                        time.sleep(1)

                        # 3. Fill CVC
                        cvc_field = wait.until(EC.element_to_be_clickable((By.ID, "cardCvc")))
                        cvc_field.clear()
                        for char in CONFIG['card_cvc']:
                            cvc_field.send_keys(char)
                            time.sleep(0.05)
                        print("✅ CVC filled")
                        time.sleep(2)

                        # Optional: Verify the billing info checkbox is checked (it should be by default)
                        try:
                            billing_checkbox = browser.find_element(By.ID, "cardUseShippingAsBilling")
                            if billing_checkbox.is_selected():
                                print("✅ Billing info same as shipping is checked")
                        except:
                            print("ℹ️ Billing checkbox not found or not checked")

                    except Exception as e:
                        print(f"❌ Card selection/filling failed: {e}")

                    time.sleep(3)

                    # 11. Click Pay Button
                    pay_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
                    pay_button.click()
                    print("✅ Pay button clicked!")
                    print("🎉 Checkout process completed!")

                    
                except Exception as form_error:
                    print(f"❌ Error filling form: {form_error}")
                    import traceback
                    traceback.print_exc()
                    
            except Exception as e:
                print(f"❌ Stripe link 404: {e}")

        except Exception as link_error:
            print(f"❌ Could not click product link: {link_error}")

except Exception as e:
    print(f"❌ Main error: {e}")
    import traceback
    traceback.print_exc()

# 12. Keep browser open for a bit to see result
print("Waiting 10 seconds before closing...")
time.sleep(10)
browser.quit()

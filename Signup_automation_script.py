import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


def setup_driver():
    driver = webdriver.Firefox()
    driver.get('https://authorized-partner.netlify.app/login')
    driver.maximize_window()
    return driver, ActionChains(driver), WebDriverWait(driver,15)

def generate_random_data():
    phone = "98123" + str(int(time.time()))[-5:]
    email = f"testuser_{int(time.time())}@yopmail.com"
    return phone, email


def click_signup_btn(action, wait):
    signup_btn = wait.until(EC.element_to_be_clickable((By.XPATH,"//a[text()='Sign Up']")))
    action.click(signup_btn).perform()
    wait.until(EC.url_contains("/register"))

def handle_continue(driver, wait):
    try:
        remember = wait.until(EC.element_to_be_clickable((By.ID,"remember")))
        ActionChains(driver).move_to_element(remember).click().perform()
    except:
        pass
    continue_btn = wait.until(EC.element_to_be_clickable((By.XPATH,"//button[text()='Continue']")))
    driver.execute_script("arguments[0].click();",continue_btn)

def signup_form(driver, wait, email, phone):
    wait.until(EC.visibility_of_element_located((By.NAME, "firstName"))).send_keys("Test")
    wait.until(EC.visibility_of_element_located((By.NAME, "lastName"))).send_keys("User")
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "phoneNumber").send_keys(phone)
    driver.find_element(By.NAME, "password").send_keys(" TestPassword@123")
    driver.find_element(By.NAME, "confirmPassword").send_keys(" TestPassword@123")
    next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
    next_btn.click()

def handle_otp(driver, wait, email):
    print("⏳ Fetching OTP automatically...")

    main_window = driver.current_window_handle

    # Open Yopmail in new tab
    driver.execute_script("window.open('https://yopmail.com/en/', '_blank');")
    driver.switch_to.window(driver.window_handles[-1])

    # Enter email (before @)
    email_input = wait.until(EC.visibility_of_element_located((By.ID, "login")))
    email_input.clear()
    email_input.send_keys(email.split("@")[0])

    # Click "Check Inbox"
    go_btn = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[@title='Check Inbox']//i | //button/i[contains(@class,'material-icons-outlined')]")
    ))
    go_btn.click()

    refresh_btn = wait.until(EC.element_to_be_clickable((By.ID, "refresh")))
    refresh_btn.click()
    time.sleep(1)

    # Wait for inbox iframe
    wait.until(EC.frame_to_be_available_and_switch_to_it("ifinbox"))

    # Refresh until email shows up
    otp_found = False
    for attempt in range(10):
        mails = driver.find_elements(By.XPATH, "//div[@class='m']")
        if mails:
            mails[0].click()
            otp_found = True
            break
        else:
            driver.switch_to.default_content()
            try:
                refresh_btn = wait.until(EC.element_to_be_clickable((By.ID, "refresh")))
                refresh_btn.click()
                time.sleep(1)
            except:
                pass
            time.sleep(1)
            driver.switch_to.frame("ifinbox")

    if not otp_found:
        print("❌ OTP email not received! Trying default OTPs...")
        driver.close()
        driver.switch_to.window(main_window)

        test_otps = ["123456", "000000", "111111", "1234", "0000"]

        for test_otp in test_otps:
            otp_field = None
            selectors = [
                (By.NAME, "otp"),
                (By.XPATH, "//input[contains(@placeholder,'OTP')]"),
                (By.XPATH, "//input[contains(@placeholder,'code')]"),
                (By.XPATH, "//input[@type='text']")
            ]

            for selector in selectors:
                try:
                    otp_field = wait.until(EC.visibility_of_element_located(selector))
                    break
                except:
                    continue

            if otp_field:
                otp_field.clear()
                otp_field.send_keys(test_otp)
                verify_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
                verify_btn.click()
                print(f"✅ Tried OTP: {test_otp}")
                time.sleep(2)

                current_url = driver.current_url
                if "otp" not in current_url.lower() and "verify" not in current_url.lower():
                    print(f"✅ Success with OTP: {test_otp}")
                    return True

        print("❌ All fallback OTPs failed")
        return False

    # Extract OTP from email
    driver.switch_to.default_content()
    wait.until(EC.frame_to_be_available_and_switch_to_it("ifmail"))

    try:
        mail_body = wait.until(EC.visibility_of_element_located((By.ID, "mail"))).text
        otp_match = re.search(r"\b\d{6}\b", mail_body) or re.search(r"\b\d{4}\b", mail_body)
        if otp_match:
            otp_code = otp_match.group(0)
            print(f"📩 OTP received: {otp_code}")
        else:
            raise Exception("OTP not found in email")
    except Exception as e:
        print(f"Error extracting OTP: {e}")
        driver.close()
        driver.switch_to.window(main_window)
        return False

    driver.close()
    driver.switch_to.window(main_window)
    time.sleep(1)

    otp_field = None
    selectors = [
        (By.NAME, "otp"),
        (By.XPATH, "//input[contains(@placeholder,'OTP')]"),
        (By.XPATH, "//input[contains(@placeholder,'code')]"),
        (By.XPATH, "//input[@type='text']"),
        (By.XPATH, "//form//input[1]")
    ]

    for selector in selectors:
        try:
            otp_field = wait.until(EC.visibility_of_element_located(selector))
            print(f"✓ Found OTP field using: {selector}")
            break
        except:
            continue

    if not otp_field:
        print("❌ Could not find OTP field after returning from Yopmail")
        return False

    try:
        driver.execute_script("arguments[0].focus();", otp_field)
        otp_field.clear()
        otp_field.send_keys(otp_code)
        print(f"✅ OTP entered: {otp_code}")

        verify_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
        driver.execute_script("arguments[0].click();", verify_btn)
        print("✅ OTP submitted automatically!")
        time.sleep(2)
        return True
    except Exception as e:
        print(f"❌ Error entering/submitting OTP: {e}")
        return False


    """" (for the manual otp)
    otp_field = None
   try:
        otp_field = wait.until(EC.visibility_of_element_located((By.NAME, "otp")))
    except:
        try:
            otp_field = wait.until(EC.visibility_of_element_located(
                (By.XPATH, "//input[contains(@placeholder,'OTP') or contains(@placeholder,'code')]")))
        except:
            otp_field = wait.until(EC.visibility_of_element_located(
                (By.XPATH, "/html/body/div[3]/div[4]/div/div/div/div[2]/div/form/div[1]/div[2]/input")))

    # Manual OTP entry
    otp_code = input("Enter OTP: ")
    otp_field.send_keys(otp_code)
    time.sleep(2)

    # Click verify
    verify_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
    verify_btn.click()
    time.sleep(4)
"""
def fill_agency_details(driver, wait):
    wait.until(EC.visibility_of_element_located((By.NAME,"agency_name"))).send_keys("Abc def")
    wait.until(EC.element_to_be_clickable((By.NAME, "role_in_agency"))).send_keys("Manger")
    wait.until(EC.visibility_of_element_located((By.NAME,"agency_email"))).send_keys("abc@test.com")
    wait.until(EC.visibility_of_element_located((By.NAME,"agency_website"))).send_keys("www.virt.com")
    wait.until(EC.visibility_of_element_located((By.NAME,"agency_address"))).send_keys("Kathmandu")

    driver.find_element(By.XPATH, "//span[contains(text(),'Select Your Region of Operation')]").click()
    time.sleep(1)

    search_box = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Search...']")))
    search_box.send_keys("Australia")
    time.sleep(1)

    australia_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Australia']")))
    driver.execute_script("arguments[0].click();", australia_option)

    time.sleep(1)

    search_box.send_keys(Keys.ESCAPE)
    time.sleep(0.5)
    driver.find_element(By.XPATH, "//body").click()

    next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
    driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
    driver.execute_script("arguments[0].click();", next_btn)  # ADD THIS CLICK
    time.sleep(1)



def professional_experiences(driver, wait):
    time.sleep(2)

    try:
        dropdown_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@id,'form-item')]")))
        dropdown_btn.click()
    except:
        pass

    one_year = wait.until(EC.element_to_be_clickable((By.XPATH,"//span[contains(text(),'1 year')]")))
    one_year.click()

    time.sleep(1)

    wait.until(EC.visibility_of_element_located((By.NAME, "number_of_students_recruited_annually"))).send_keys("10")
    wait.until(EC.visibility_of_element_located((By.NAME, "focus_area"))).send_keys("Graduate to australia")
    wait.until(EC.visibility_of_element_located((By.NAME, "success_metrics"))).send_keys("70")
    wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(text(),'Career Counseling')]"))).click()

    next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
    next_btn.click()
    time.sleep(2)

def verification_and_preferences(driver, wait):

    wait.until(EC.visibility_of_element_located((By.NAME,"business_registration_number"))).send_keys('2244')

    preferred_countries = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@class='font-satoshi-regular text-translucent']")))
    preferred_countries.click()
    time.sleep(1)

    # Search for Australia
    search_box = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Search...']")))
    search_box.send_keys("Australia")
    time.sleep(1)

    # Click Australia option
    australia_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Australia']")))
    driver.execute_script("arguments[0].click();", australia_option)
    search_box.send_keys(Keys.ESCAPE)
    time.sleep(1)

    wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(text(),'Universities')]"))).click()
    time.sleep(1)

    wait.until(EC.visibility_of_element_located((By.NAME,"certification_details"))).send_keys("abcd")

    upload_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
    upload_input.send_keys(r"C:\Users\Luna\Desktop\Quality Assurance Certificate.png")
    try:
        submit_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@type='submit'] | //button[contains(text(),'Submit')]")))
        driver.execute_script("arguments[0].click();", submit_btn)
    except:
        pass

def main():
    driver, action, wait = setup_driver()
    phone, email = generate_random_data()

    print(f"Using: {email} | {phone}")

    try:
        click_signup_btn(action, wait)
        handle_continue(driver, wait)
        signup_form(driver, wait, email, phone)
        handle_otp(driver, wait, email)
        fill_agency_details(driver, wait)
        professional_experiences(driver, wait)
        verification_and_preferences(driver, wait)

        print("Signup completed!")
        print(f"Used: {phone} | {email}")

    except Exception as e:
        print(f"Error: {e}")

    input("Press Enter to close...")



if __name__ == "__main__":
    main()






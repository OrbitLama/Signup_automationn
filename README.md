# Signup_automationn
Automated signup script using Selenium to handle form submission and OTP verification, with test report
Signup Automation Script



Overview : 
This project automates the signup process on Authorized Partner Signup Page using Selenium WebDriver.
The automation covers:

-Flling signup forms
-OTP verification (auto-fetch from Yopmail)
-Agency details
-Professional experience

Verification and preferences including file upload

Prerequisites
-Python 3.10+
-Selenium 4.x
-Firefox 117 or Chrome latest version
-GeckoDriver (for Firefox) or ChromeDriver (for Chrome)
-Internet connection

Setup

Clone the repository:

git clone https://github.com/OrbitLama/signup_automation_task.git
cd signup_automation_task


Install required packages:
pip install selenium

Make sure GeckoDriver (or ChromeDriver) is in your PATH or in the project folder.

How to Run
python signup_automation_script.py


The script will open the browser, navigate to the signup page, and fill all required fields.

OTP is automatically fetched from Yopmail; fallback OTPs are tried if email fails.

After completing all steps, the script waits for your confirmation to close the browser.

Test Data / Accounts

Emails: Automatically generated via timestamp (e.g., testuser_1695700000@yopmail.com)

Phone: Auto-generated using timestamp

Password: TestPassword@123

Agency details: Test Agency, Manager, agency@test.com

Uploaded document: Quality Assurance Certificate.png



[test_report.xlsx](https://github.com/user-attachments/files/22566200/test_report.xlsx)

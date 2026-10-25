#!/usr/bin/env python3
"""
Gmail Account Creator - Handles actual Gmail account creation
Uses undetected-chrome to bypass Google's detection
"""

import asyncio
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import undetected_chrome as uc
import random
import string

logger = logging.getLogger(__name__)

class GmailCreator:
    """Handles Gmail account creation via Selenium"""
    
    def __init__(self):
        self.driver = None
    
    async def check_username_availability(self, username: str) -> bool:
        """Check if Gmail username is available"""
        try:
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # Use undetected-chrome
            self.driver = await asyncio.to_thread(
                uc.Chrome,
                options=options,
                version_main=None
            )
            
            self.driver.get("https://accounts.google.com/signup/v2/webcreateaccount")
            await asyncio.sleep(2)
            
            wait = WebDriverWait(self.driver, 15)
            
            # Fill basic info to get to username check
            first_name = wait.until(EC.presence_of_element_located((By.ID, "firstName")))
            first_name.send_keys("Test")
            await asyncio.sleep(0.5)
            
            last_name = self.driver.find_element(By.ID, "lastName")
            last_name.send_keys("User")
            await asyncio.sleep(0.5)
            
            self.driver.find_element(By.ID, "collectNameNext").click()
            await asyncio.sleep(3)
            
            # Birthday
            month = self.driver.find_element(By.ID, "month")
            month.send_keys("01")
            day = self.driver.find_element(By.ID, "day")
            day.send_keys("15")
            year = self.driver.find_element(By.ID, "year")
            year.send_keys("1990")
            
            self.driver.find_element(By.ID, "collectBirthdayNext").click()
            await asyncio.sleep(3)
            
            # Username check
            username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
            username_field.send_keys(username)
            await asyncio.sleep(1)
            
            self.driver.find_element(By.ID, "collectEmailNext").click()
            await asyncio.sleep(3)
            
            # Check if username is taken
            try:
                self.driver.find_element(By.XPATH, "//*[contains(text(), 'unavailable')]")
                logger.info(f"Username {username} is taken")
                return False
            except:
                logger.info(f"Username {username} is available")
                return True
                
        except Exception as e:
            logger.error(f"Error checking username: {str(e)}")
            return False
        finally:
            if self.driver:
                self.driver.quit()
    
    async def suggest_available_usernames(self, base_username: str, count: int = 5) -> list:
        """Suggest available alternative usernames"""
        suggestions = []
        
        for i in range(count):
            # Add random numbers to base
            variant = f"{base_username}{random.randint(1, 9999)}"
            is_available = await self.check_username_availability(variant)
            
            if is_available:
                suggestions.append(variant)
            
            if len(suggestions) >= count:
                break
        
        return suggestions[:count]
    
    async def create_gmail_account(self, first_name: str, last_name: str, 
                                  email: str, password: str, dob: str) -> dict:
        """Create a real Gmail account"""
        try:
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Use undetected-chrome
            self.driver = await asyncio.to_thread(
                uc.Chrome,
                options=options,
                version_main=None
            )
            
            self.driver.get("https://accounts.google.com/signup/v2/webcreateaccount")
            await asyncio.sleep(2)
            
            wait = WebDriverWait(self.driver, 20)
            
            logger.info(f"[{email}] Creating account...")
            
            # Step 1: Name
            logger.info(f"[{email}] Filling name...")
            first_field = wait.until(EC.presence_of_element_located((By.ID, "firstName")))
            first_field.clear()
            first_field.send_keys(first_name)
            await asyncio.sleep(0.5)
            
            last_field = self.driver.find_element(By.ID, "lastName")
            last_field.clear()
            last_field.send_keys(last_name)
            await asyncio.sleep(0.5)
            
            self.driver.find_element(By.ID, "collectNameNext").click()
            await asyncio.sleep(3)
            
            # Step 2: Birthday
            logger.info(f"[{email}] Filling birthday...")
            day, month, year = dob.split('/')
            
            month_field = wait.until(EC.presence_of_element_located((By.ID, "month")))
            month_field.send_keys(month)
            await asyncio.sleep(0.3)
            
            day_field = self.driver.find_element(By.ID, "day")
            day_field.send_keys(day)
            await asyncio.sleep(0.3)
            
            year_field = self.driver.find_element(By.ID, "year")
            year_field.send_keys(year)
            await asyncio.sleep(0.3)
            
            gender_select = self.driver.find_element(By.ID, "genderSelect")
            gender_select.click()
            await asyncio.sleep(0.5)
            
            genders = ["Male", "Female", "Rather not say"]
            gender_opt = self.driver.find_element(
                By.XPATH, 
                f"//option[text()='{random.choice(genders)}']"
            )
            gender_opt.click()
            await asyncio.sleep(0.5)
            
            self.driver.find_element(By.ID, "collectBirthdayNext").click()
            await asyncio.sleep(3)
            
            # Step 3: Username
            logger.info(f"[{email}] Setting username...")
            username = email.split("@")[0]
            username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
            username_field.clear()
            username_field.send_keys(username)
            await asyncio.sleep(0.5)
            
            self.driver.find_element(By.ID, "collectEmailNext").click()
            await asyncio.sleep(4)
            
            # Check if email taken
            try:
                self.driver.find_element(By.XPATH, "//*[contains(text(), 'unavailable')]")
                return {
                    "success": False,
                    "error": "Username already taken"
                }
            except:
                pass
            
            # Step 4: Password
            logger.info(f"[{email}] Setting password...")
            pwd_field = wait.until(EC.presence_of_element_located((By.ID, "passwd")))
            pwd_field.send_keys(password)
            await asyncio.sleep(0.5)
            
            pwd_confirm = self.driver.find_element(By.ID, "passwdConfirm")
            pwd_confirm.send_keys(password)
            await asyncio.sleep(0.5)
            
            self.driver.find_element(By.ID, "collectPasswordNext").click()
            await asyncio.sleep(4)
            
            # Step 5: Skip recovery
            logger.info(f"[{email}] Skipping recovery email...")
            try:
                skip_recovery = wait.until(
                    EC.element_to_be_clickable((By.ID, "collectRecoverySkip")),
                    timeout=10
                )
                skip_recovery.click()
                await asyncio.sleep(2)
            except:
                pass
            
            # Step 6: Skip phone
            logger.info(f"[{email}] Skipping phone verification...")
            try:
                skip_phone = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(text(), 'Skip')]")
                    ),
                    timeout=10
                )
                skip_phone.click()
                await asyncio.sleep(2)
            except:
                pass
            
            # Step 7: Accept terms
            logger.info(f"[{email}] Accepting terms...")
            try:
                agree_btn = wait.until(
                    EC.element_to_be_clickable((By.ID, "iagree")),
                    timeout=10
                )
                agree_btn.click()
                await asyncio.sleep(3)
            except:
                pass
            
            logger.info(f"[{email}] ✅ Account created successfully")
            
            return {
                "success": True,
                "email": email,
                "password": password
            }
            
        except Exception as e:
            logger.error(f"[{email}] Account creation error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            if self.driver:
                self.driver.quit()

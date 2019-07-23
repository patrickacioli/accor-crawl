import scrapy
import time
import random
import pandas as pd 
from bs4 import BeautifulSoup

# Selenium webdriver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options  
chrome_options = Options()  
chrome_options.add_argument("--headless")  
chrome_options.add_argument("--no-sandbox")  


class RegisterSpider(scrapy.Spider):

    name = "register"
    start_urls = [
        "https://www.accorhotels.com/authentication/index.pt-br.shtml#/register",

    ]

    def start_requests(self):
        yield scrapy.Request(
            self.start_urls[0],
            callback=self.parse
        )

    def parse(self, response):

        cads = pd.read_csv("cadastros.csv")

        for i, cad in cads.iterrows():
            self.driver = webdriver.Chrome(chrome_options=chrome_options)  
            self.driver.get(self.start_urls[0])        
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "cnil-banner__action-close")))
            self.driver.find_element_by_id("cnil-banner__action-close").click()

            email     = cad["email"]
            password  = cad["password"]
            firstName = cad["first_name"]
            lastName  = cad["last_name"]

            self.driver.get(self.start_urls[0])        
               
            self.driver.find_element_by_name("email").send_keys(email)
            self.driver.find_element_by_name("password").send_keys(password)                
            self.driver.find_element_by_name("firstName").send_keys(firstName)                
            self.driver.find_element_by_name("lastName").send_keys(lastName)                
                

            el = self.driver.find_element_by_name("civility")
            for option in el.find_elements_by_tag_name("option"):
                if option.get_attribute("value") == "MR":
                    option.click()
                    break        
            el = self.driver.find_element_by_name("country")
            for option in el.find_elements_by_tag_name("option"):
                if option.get_attribute("value") == cad["country"]:
                    option.click()
                    break        
            el = self.driver.find_element_by_name("states")
            for option in el.find_elements_by_tag_name("option"):
                if option.get_attribute("value") == cad["state"]:
                    option.click()
                    break        
            
            self.driver.find_element_by_class_name("api__button").click()        

            try: 
                WebDriverWait(self.driver, 60).until(EC.invisibility_of_element((By.CLASS_NAME, "api__button")))
                self.driver.get("https://secure.accorhotels.com/account/index.html#/pt-br/loyalty/advantageCards")
                WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, "ahAdvantageCard__data__num")))
                result_page = BeautifulSoup(self.driver.page_source, "html.parser")
                code = result_page.find("div", class_="ahAdvantageCard__data__num").find("span").text                
            except Exception:
                code = "NULL"
            
            yield {
                "code"     : code,
                "email"    : email,
                "password" : password
            }

            self.driver.close()


            
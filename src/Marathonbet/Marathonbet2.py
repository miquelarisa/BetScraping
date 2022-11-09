from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time


class Marathonbet2():

    def __init__(self):

        self.tennis_url = 'https://www.marathonbet.es/es/popular/Tennis'

        PATH = '..\..\Drivers\chromedriver.exe'
        self.driver = webdriver.Chrome(PATH)
        self.timeout = 1

        # Go to the tennis page and maximize the window.
        self.driver.get(self.tennis_url)
        self.driver.maximize_window()
        self.scrap_tennis_data()


    def scrap_tennis_data(self):

        # Load all the dynamic data and get all match links
        self.scroll_to_load_all_data()
        page_links = self.get_all_match_links()
        print(len(page_links))

        # Iterate each match.
        for extension in page_links:

            # Go to the current match.
            link = self.tennis_url + extension
            self.go_to_link(link)
            self.click_on_all_markets()

            # Find if the current match is a doubles match, and get its players.
            is_doubles = 'Doubles' in link
            players = self.find_players(is_doubles)
            print(players[0], players[1])

            # Create the match and start iterating all the bets


    def go_to_link(self, link):

        self.driver.get(link)
        time.sleep(self.timeout)

        '''try:
            element_present = EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Todos los mercados')]"))
            WebDriverWait(self.driver, self.timeout).until(element_present)
        except TimeoutException:
            print('Timed out waiting for page to load')'''


    def get_all_match_links(self):

        # Find all the rows of each individual event.
        events = self.driver.find_element(By.ID, 'events_content')
        rows = events.find_elements(By.CLASS_NAME, 'coupon-row')

        # Prepare the output.
        pageLinks = list()

        # For each row, find the link and add it to the list.
        for row in rows:

            table = row.find_element(By.CLASS_NAME, 'coupon-row-item')
            links = table.find_elements(By.CLASS_NAME, 'member-link')

            link = links[0].get_attribute('href')
            pageLinks.append(link)

        return pageLinks


    def find_players(self, is_doubles = False):

        players = self.driver.find_elements(By.CLASS_NAME, 'member-link')
        local = players[0].find_element(By.TAG_NAME, 'span').text
        visitor = players[1].find_element(By.TAG_NAME, 'span').text

        return [local, visitor]


    def click_on_all_markets(self):

        all_markets = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Todos los mercados')]")
        if len(all_markets) > 0:
            all_markets_button = all_markets[0].find_element(By.XPATH, '..')
            all_markets_button.click()


    def scroll_to_load_all_data(self):

        endtime = time.time() + 10
        while time.time() < endtime:
            footer = self.driver.find_elements(By.ID, 'footer')
            self.driver.execute_script("window.scrollTo(arguments[0])", footer)

            '''footer = self.driver.find_elements(By.CLASS_NAME, 'footer-menu__text')
            self.driver.execute_script("arguments[0].scrollIntoView;", footer)'''
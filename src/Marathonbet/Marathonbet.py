from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from datetime import datetime
from src.Utility import *

import time


class Marathonbet():

    def __init__(self):

        self.tennis_url = 'https://www.marathonbet.es/es/popular/Tennis'
        self.betting_site = 'Marathonbet'

        PATH = '..\..\Drivers\chromedriver.exe'
        self.driver = webdriver.Chrome(PATH)
        self.timeout = 1

        self.interesting_markets = ["Gana el partido con hándicap de sets", "Gana el partido con hándicap de juegos",
            "Total de sets", "Total de juegos", "Total de tie-breaks", "Total de juegos ganados (Local)",
            "Total de juegos ganados (Visitor)", "Resultado del 1.er set", "Gana el 1.er set con hándicap",
            "Total de juegos - 1.er set", "Total de juegos ganados (Local) - 1.er set", "Total de juegos ganados (Visitor) - 1.er set",
            "Resultado del 2.º set", "Gana el 2.º set con hándicap", "Total de juegos - 2.º set", "Total de juegos ganados (Local) - 2.º set",
            "Total de juegos ganados (Visitor) - 2.º set", "Resultado del 3.er set", "Gana el 3.er set con hándicap", "Total de juegos - 3.er set",
            "Total de juegos ganados (Local) - 3.er set", "Total de juegos ganados (Visitor) - 3.er set", "Más aces con hándicap", "Total de aces",
            "Más doble faltas con hándicap", "Total de dobles faltas"]

        # Pandas dataframe where the scrapped data will be stored
        self.scrapped_data = pd.DataFrame()
        # Go to the tennis page and maximize the window.
        self.driver.get(self.tennis_url)
        self.driver.maximize_window()
        # Close cookies popup
        self.close_cookies_popup()
        # Scrap the data
        self.scrap_tennis_data()
        # Generate CSV from dataframe
        # TODO: Change filepath (user input?)
        self.scrapped_data.to_csv('C:\\Temp\\test.csv', index=False)

    def scrap_tennis_data(self):

        match_dataset = {}
        sport = 'Tennis'

        # Load all the dynamic data and get all match links
        self.scroll_to_load_all_data_v3(30, 1)
        page_links = self.get_all_match_links()
        print(len(page_links))

        # TODO: Delete Test iterator limit
        i = 0

        # Iterate each match.
        for extension in page_links:

            # Go to the current match.
            #link = self.tennis_url + extension
            link = extension
            # TODO: Timeout 1s abans de carregar següent pàgina
            self.go_to_link(link)
            self.click_on_all_markets()

            # Find if the current match is a doubles match, and get its players.
            is_doubles = 'Doubles' in link
            players = self.find_players(is_doubles)

            # Create the match and start iterating all the bets
            #betting_set = self.get_betting_dataset(players[0], players[1])
            match_bets_df = self.get_betting_dataset_v2(players[0], players[1], sport)

            #match_dataset[players[0] + ' vs ' + players[1]] = betting_set
            # If main dataframe is empty, assign it to match dataframe
            if self.scrapped_data.empty:
                self.scrapped_data = match_bets_df
            # If it has data, use 'concat' to concatenate match to main dataframe
            else:
                self.scrapped_data = pd.concat([self.scrapped_data, match_bets_df], ignore_index=True, sort=False)

            # TODO: Delete Test iterator limit
            i += 1
            if i == 10:
                break

        #print(match_dataset)


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


    def get_betting_dataset(self, local, visitor):

        betting_dataset = {}

        # Find all markets of the page.
        markets = self.driver.find_elements(By.CLASS_NAME, 'market-inline-block-table-wrapper')

        # For each market:
        for market in markets:

            # Get the name of the market.
            name = market.find_element(By.CLASS_NAME, 'name-field').text
            name = name.replace(local, 'Local')
            name = name.replace(visitor, 'Visitor')

            # If it should be processed.
            if name in self.interesting_markets:

                # Find all bets.
                bets = market.find_elements(By.CLASS_NAME, 'selection-link')

                # And for each bet:
                for bet in bets:

                    # Get the key of the bet and find the substring after @.
                    key = bet.get_attribute('data-selection-key')
                    key = key[key.find('@')+1:]

                    # Get the value and yield the current bet.
                    value = bet.get_attribute('data-selection-price')

                    aux_info_value = bet.find_element(By.XPATH, '..').find_element(By.XPATH, '..')
                    aux_info_value = aux_info_value.find_elements(By.CLASS_NAME, 'coeff-value')
                    if len(aux_info_value) > 0 and 'Handicap' in key:
                        if key[-1] == 'H':
                            key = key[:-1] + '(Local)'
                        elif key[-1] == 'A':
                            key = key[:-1] + '(Visitor)'
                        key = key + aux_info_value[0].text

                    betting_dataset[key] = value

        return betting_dataset

    def get_betting_dataset_v2(self, local, visitor, sport):

        market_list = []
        bet_list = []
        quote_list = []
        scrap_datetime_list = []

        event = local + ' vs ' + visitor

        betting_dataset = {}

        # Find all markets of the page.
        markets = self.driver.find_elements(By.CLASS_NAME, 'market-inline-block-table-wrapper')

        # For each market:
        for market in markets:

            # Get the name of the market.
            name = market.find_element(By.CLASS_NAME, 'name-field').text
            name = name.replace(local, 'Local')
            name = name.replace(visitor, 'Visitor')

            # If it should be processed.
            if name in self.interesting_markets:

                # Find all bets.
                bets = market.find_elements(By.CLASS_NAME, 'selection-link')

                # And for each bet:
                for bet in bets:
                    # Get the key of the bet and find the substring after @.
                    key = bet.get_attribute('data-selection-key')
                    key = key[key.find('@') + 1:]

                    # Get the value and yield the current bet.
                    value = bet.get_attribute('data-selection-price')

                    aux_info_value = bet.find_element(By.XPATH, '..').find_element(By.XPATH, '..')
                    aux_info_value = aux_info_value.find_elements(By.CLASS_NAME, 'coeff-value')
                    if key[-1] == 'H':
                        key = key[:-1] + '(Local)'
                    elif key[-1] == 'A':
                        key = key[:-1] + '(Visitor)'
                    if len(aux_info_value) > 0 and 'Handicap' in key:
                        key = key + aux_info_value[0].text

                    betting_dataset[key] = value

                    market_list.append(key[:key.find('.')])
                    bet_list.append(key[key.find('.') + 1:])
                    quote_list.append(value)
                    scrap_datetime_list.append(datetime.utcnow())

        return generate_event_dataframe(self.betting_site, sport, event, local, visitor, market_list, bet_list,
                                        quote_list, scrap_datetime_list)

    def scroll_to_load_all_data(self):

        endtime = time.time() + 3
        while time.time() < endtime:
            footer = self.driver.find_elements(By.ID, 'footer')
            self.driver.execute_script("window.scrollTo(arguments[0])", footer)

            '''footer = self.driver.find_elements(By.CLASS_NAME, 'footer-menu__text')
            self.driver.execute_script("arguments[0].scrollIntoView;", footer)'''

    def scroll_to_load_all_data_v2(self):

        # Maximum time allowed (s) for endless scrolling
        scroll_timeout = 30
        endtime = time.time() + scroll_timeout

        # Main container element where the scroll will be performed
        '''main_container = self.driver.find_element(By.ID, 'main_container')middle-container
        main_container = self.driver.find_element(By.CLASS_NAME, 'grid-middle')'''
        main_container = self.driver.find_element(By.ID, 'middle-container')
        '''self.driver.execute_script("arguments[0].scrollIntoView();", main_container)'''


        # Current scroll height
        loaded_height_old = self.driver.execute_script("return arguments[0].scrollHeight", main_container)
        loaded_height = self.driver.execute_script("return document.querySelector('#middle-container').scrollHeight")

        while time.time() < endtime:
            # Scroll to the bottom of the loaded section
            '''self.driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", main_container)'''
            '''self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", main_container)'''
            self.driver.execute_script("arguments[0].scrollBy(0, 4000);", main_container)
            '''self.driver.execute_script("document.querySelector('#middle-container').scrollBy(0, 200);")'''
            # Time allowed (s) to load the next section
            time.sleep(1)
            # New scroll height
            new_height = self.driver.execute_script("return arguments[0].scrollHeight", main_container)
            # Check if the ending of the page has been reached (no difference in height from last scroll)
            '''if new_height == loaded_height:
                break'''
            loaded_height = new_height
        '''
        # Current scroll height
        loaded_height = self.driver.execute_script("return document.body.scrollHeight")

        while time.time() < endtime:
            # Scroll to the bottom of the loaded section
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Time allowed (s) to load the next section
            time.sleep(1)
            # New scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            # Check if the ending of the page has been reached (no difference in height from last scroll)
            if new_height == loaded_height:
                break
            loaded_height = new_height'''

    def scroll_to_load_all_data_v3(self, scroll_timeout, load_time):
        # scroll_timeout: Maximum time allowed (s) for endless scrolling
        # load_time: Time allowed (s) to load the next section

        # Scroll timeout
        endtime = time.time() + scroll_timeout
        # Footer element
        footer = self.driver.find_element(By.ID, "footer")
        # Main container, with the dynamic scroll
        main_container = self.driver.find_element(By.ID, 'middle-container')
        # Current scroll height
        loaded_height = self.driver.execute_script("return arguments[0].scrollHeight", main_container)

        while time.time() < endtime:
            # Scroll to the bottom of the loaded section, with the help of the footer element
            self.driver.execute_script("arguments[0].scrollIntoView();", footer)
            # Wait time to load the next section after the scroll
            time.sleep(load_time)
            # Once the scroll reaches the footer, the next section will be automatically loaded and the footer will
            #   move once again to the bottom of the page.
            # New scroll height
            new_height = self.driver.execute_script("return arguments[0].scrollHeight", main_container)
            # Check if the ending of the page has been reached (no difference in height from last scroll)
            if new_height == loaded_height:
                break
            loaded_height = new_height

    def close_cookies_popup(self):

        # Find the cookies popup
        cookies_popup = self.driver.find_elements(By.CLASS_NAME, 'cookie-notice')

        # If no popup is found, exit function
        if len(cookies_popup) == 0:
            return

        # Close the popup accepting the cookies
        cookies_popup[0].find_element(By.TAG_NAME, 'button').click()
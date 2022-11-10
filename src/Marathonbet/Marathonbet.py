from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time


class Marathonbet():

    def __init__(self):

        self.tennis_url = 'https://www.marathonbet.es/es/popular/Tennis'

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

        # Go to the tennis page and maximize the window.
        self.driver.get(self.tennis_url)
        self.driver.maximize_window()
        self.scrap_tennis_data()


    def scrap_tennis_data(self):

        match_dataset = {}

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

            # Create the match and start iterating all the bets
            betting_set = self.get_betting_dataset(players[0], players[1])

            match_dataset[players[0] + ' vs ' + players[1]] = betting_set


        print(match_dataset)



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


    def scroll_to_load_all_data(self):

        endtime = time.time() + 3
        while time.time() < endtime:
            footer = self.driver.find_elements(By.ID, 'footer')
            self.driver.execute_script("window.scrollTo(arguments[0])", footer)

            '''footer = self.driver.find_elements(By.CLASS_NAME, 'footer-menu__text')
            self.driver.execute_script("arguments[0].scrollIntoView;", footer)'''
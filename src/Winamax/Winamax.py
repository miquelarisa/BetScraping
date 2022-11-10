from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time


class Winamax():

    def __init__(self):

        self.tennis_url = 'https://www.winamax.es/apuestas-deportivas/sports/5'

        PATH = '..\..\Drivers\chromedriver.exe'
        self.driver = webdriver.Chrome(PATH)
        self.timeout = 1

        self.interesting_markets = ["Ganador", "Total juegos", "Gana al menos un set (Local)", "Gana al menos un set (Visitor)",
        "Hándicap de juegos", "1er set - Ganador", "2º set - Ganador", "3er set - Ganador", "1er set - Total de juegos", "2º set - Total de juegos",
        "3er set - Total de juegos", "1er set - Hándicap de juegos", "2º set - Hándicap de juegos", "3er set - Hándicap de juegos", "Total de juegos de (Local)",
        "Total de juegos de (Visitor)", "Hándicap de Sets", "Cualquier set a cero"]

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
        for link in page_links:
            # Go to the current match.
            self.go_to_link(link)

            live = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Pts')]")
            if len(live) == 0:

                # Find if the current match is a doubles match, and get its players.
                players = self.find_players()

                # Create the match and start iterating all the bets
                if len(players):
                    betting_set = self.get_betting_dataset(players[0], players[1])

    def go_to_link(self, link):

        self.driver.get(link)
        time.sleep(self.timeout)


    def get_all_match_links(self):

        # Find all the rows of each individual event.
        events = self.driver.find_element(By.XPATH, "//div[@data-testid='middleColumn']")
        rows = events.find_elements(By.CLASS_NAME, 'sc-gUXlfm')

        # Prepare the output.
        pageLinks = list()

        # For each row, find the link and add it to the list.
        for row in rows:
            table = row.find_element(By.CLASS_NAME, 'sc-dkzDqf')
            link = table.get_attribute('href')
            pageLinks.append(link)

        return pageLinks


    def find_players(self):

        local = ''
        visitor = ''
        players = self.driver.find_elements(By.CLASS_NAME, 'sc-jWEIYm')
        if len(players) > 0:
            local = players[0].text
            visitor = players[1].text

        return [local, visitor]

    def click_on_all_markets(self):
        pass


    def get_betting_dataset(self, local, visitor):

        betting_dataset = {}

        # Find all markets of the page.
        markets = self.driver.find_elements(By.CLASS_NAME, 'sc-jQcEE')

        # For each market:
        for market in markets:

            # Get the name of the market.
            name = market.find_element(By.CLASS_NAME, 'sc-gLLjfg').text
            if name.find('\n') > -1:
                name = name[: name.find('\n')]

            # If it should be processed.
            if name in self.interesting_markets:

                # Find all bets.
                bets = market.find_elements(By.CLASS_NAME, 'bet-group-outcome-odd')

                # And for each bet:
                for bet in bets:
                    # Get the key of the bet.
                    key = bet.find_elements(By.CLASS_NAME, 'sc-bcfbLH')
                    if len(key) > 0:
                        key = key[0].text
                        key = name + ' ' + key

                    # Get the value and yield the current bet.
                    value = bet.find_elements(By.CLASS_NAME, 'sc-bmyKNl')
                    if len(value) > 0:
                        value = value[0].text

                    print(key, value)

    def scroll_to_load_all_data(self):
        pass
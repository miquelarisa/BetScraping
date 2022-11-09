from bs4 import BeautifulSoup
import requests

from selenium import webdriver
import time

class Marathonbet():

    def __init__(self):
        pass


    def scrap_tennis_data(self):

        # Go to the tennis page
        tennis_url = 'https://www.marathonbet.es/es/popular/Tennis'
        tennis_page = requests.get(tennis_url)
        general_soup = BeautifulSoup(tennis_page.content, 'html.parser')

        # Load all the dynamic data and get all match links
        self.scroll_to_load_all_data(tennis_url, tennis_page, general_soup)
        page_links = self.get_all_match_links(general_soup)
        print(len(page_links))

        # Iterate each match
        for extension in page_links:
    
            # Go to current match
            link = tennis_url + extension
            match_page = requests.get(link)
            match_soup = BeautifulSoup(match_page.content, 'html.parser')
            self.click_on_all_markets(match_soup)
    
            # Find if the current match is a doubles match, and get its players.
            is_doubles = 'Doubles' in link
            players = self.find_players(match_soup, is_doubles)
            print(players[0], players[1])

            # Create the match and start iterating all the bets


    def find_players(self, soup, is_doubles = False):

        players = soup.find_all(class_='member-link')
        local = players[0].find('span').text
        visitor = players[1].find('span').text

        return [local, visitor]


    def get_all_match_links(self, soup):

        # Find all the rows of each individual event.
        events = soup.find(id='events_content')
        rows = events.find_all(class_='coupon-row')

        # Prepare the output.
        page_links = list()

        # From each row, find the link and add it to the list.
        for row in rows:
            table = row.find(class_='coupon-row-item')
            links = table.find_all(class_='member-link')

            link = links[0]['href']
            page_links.append((link))

        return page_links


    def click_on_all_markets(self, soup):

        all_markets = soup.find_all('div', class_='text-field')
        if len(all_markets) > 0:
            all_markets_button = all_markets[0].parent
            all_markets_button.click


    def scroll_to_load_all_data(self, tennis_url, tennis_page, general_soup):
        pass # Sha de fer tot el metode de scroll de la pagina dinamica perque agafi tots els partits
"""
        driver = webdriver.Chrome(executable_path=r"E:\Chromedriver\chromedriver_win32_chrome83\chromedriver.exe")
        driver.get(tennis_url)
        time.sleep(2)  # Allow 2 seconds for the web page to open
        scroll_pause_time = 1  # You can set your own pause time. My laptop is a bit slow so I use 1 sec
        screen_height = driver.execute_script("return window.screen.height;")  # get the screen height of the web
        i = 1

        while True:
            # scroll one screen height each time
            driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))
            i += 1
            time.sleep(scroll_pause_time)
            # update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
            scroll_height = driver.execute_script("return document.body.scrollHeight;")
            # Break the loop when the height we need to scroll to is larger than the total scroll height
            if (screen_height) * i > scroll_height:
                break
"""
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
import time


@staticmethod
def generate_event_dataframe(betting_site, sport, event, local, visitor, market, bet, quote, scrap_datetime):
    # Generate Dataframe from dictionary of lists
    #   BettingSite: Betting site name
    #   Sport: Sport name
    #   Event: Event description
    #   Local: Local player/team name
    #   Visitor: Visitor player/team name
    #   Market: Markets for current event
    #   Bet: Bets for each market
    #   Value: Bet quotes
    #   ScrapDateTime: Date and time from when the data was scrapped

    # Pandas allows mixing lists and constant values when creating a dataset using a dictionary of lists, so instead
    #   of passing a list for each parameter, constant values can be passed for those that will be the same for
    #   all rows of the generated dataframe, e.g. all the constant fields for an event (betting_site, sport, etc.)
    dictionary_of_lists = {
        'BettingSite': betting_site,
        'Sport': sport,
        'Event': event,
        'Local': local,
        'Visitor': visitor,
        'Market': market,
        'Bet': bet,
        'Quote': quote,
        'ScrapDateTime': scrap_datetime
    }
    match_bets_df = pd.DataFrame(dictionary_of_lists)

    return match_bets_df


@staticmethod
def get_driver_path():
    # Returns path where the WebDriver is located
    return os.path.join('..', '..', 'Drivers', 'chromedriver.exe')


@staticmethod
def get_dataset_file_path():
    # Returns file path where the resulting dataset will be stored
    return os.path.join('..', 'dataset', 'bet_quotes_dataset_' + datetime.utcnow().strftime('%Y%m%d%H%M%S') + '.csv')


@staticmethod
def print_user_agent(selenium_driver):
    # Prints user_agent information
    user_agent = selenium_driver.execute_script("return navigator.userAgent")
    print('user-agent: ' + user_agent)

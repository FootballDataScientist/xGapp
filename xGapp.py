"""
# My first app
Here's our first attempt at using data to create a table:
"""

import streamlit as st
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup, Comment
import requests
import re

#shots_team1 = [0.01, 0.02, 0.07, 0.15, 0.03, 0.05, 0.07, 0.15, 0.03]
#shots_team2 = [0.2, 0.78]

url = st.text_input("Provide a link to fbref game", 'This is a place for the link')

if len(url)>0:
    def try_caption(a):
        try:
            return(a.find('caption').get_text())
        except:
            return('None')

    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'lxml')
        tables = soup.find_all('table')
        table_names = [try_caption(tab) for tab in tables]
        pandas_tables = pd.read_html(url)
        shots_table = [pandas_tables[i] for i in range(len(table_names)) if table_names[i] == 'Shots Table'][0]
        shots_table.columns = [f'{x[0]} {x[1]}' if "Unnamed" not in x[0] else x[1] for x in shots_table.columns]
        shots_table = shots_table[~shots_table.Player.isnull()]
    except:
        shots_table = 'There is no shots available in this link'

    st.write('You want to analyze ', url, ' game')

    st.write(shots_table)

#x = st.slider('x')  # 👈 this is a widget


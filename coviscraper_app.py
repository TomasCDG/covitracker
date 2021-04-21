import streamlit as st
import base64
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time
from coviscraper.coviscraper import *


st.set_page_config(page_title='CoviScaper',page_icon = ':mapamundi:', layout = 'centered')


st.title('Homemade Covid Tracker')

st.subheader('Global Covid data updated from *Worldometers.info*')

st.markdown('**_Source_** : https/:/www.worldometers.info/coronavirus/')

radio = st.radio("Which day's stats will you scrape?", ['today','yesterday'])

if radio == 'today':  #I know I should have change this before, but I'm too lazy
	def makesoup(url):
	    ''' connect and get the soup from the page'''
	    response = requests.get(url)
	    soup= BeautifulSoup(response.content, "html.parser")
	    soup =soup.select('#nav-today')[0]#.find_all('td')
	    return soup
else:
	def makesoup(url):
	    ''' connect and get the soup from the page'''
	    response = requests.get(url)
	    soup= BeautifulSoup(response.content, "html.parser")
	    soup =soup.select('#nav-yesterday')[0]#.find_all('td')
	    return soup


url = 'https://www.worldometers.info/coronavirus/'


soup = makesoup(url)
data = get_data(soup)
countries = get_country_names(soup)
indexes = get_country_indexes(soup, countries)
pops = get_pops(soup)






a='Select one country'
b='See top countries by number of cases'
options = st.radio('What would you like to see?' , (a, b))




if options == a:

	st.text('in progress')
	
	sorted_countries = list(indexes.keys()) #to prevent any problem with the countries list
	sorted_countries.sort()
	chosen_country = st.selectbox('select the country you want to scrape', sorted_countries)
	
	if st.button(f'get the data from {chosen_country}!', key='countrybutton'):
		df = df_country(soup,chosen_country, indexes)
		st.dataframe(df)

		st.text_area('',"""Warning, some fields may be missing (NA), mostly the new cases, this is because the
corresponding data has not been upgraded yet. Data is upgraded daily in different intervals, 
so earlier in the morning the dataframe will be very sparse.
Don't panic. Just come back later in the day. Or check the source to see if there's 
an error there.""")





if options == b:
	
	st.subheader('please select how many countries with most cases you want to see. ')
	n_countries = st.number_input(label = "Top 'x' countries :", value= 10 , min_value =  1, max_value = len(countries))
	
	world_index = get_world_index(soup)

	df = df_top_countries(soup, n_countries) #gets the country data

	styled_df = styler(df)
	st.dataframe(styled_df )
	st.write('_click on the uppper right of the table to maximize_')
	
	

	st.text_area('',"""Warning, some fields may be missing (NA), mostly the new cases, this is because the
corresponding data has not been upgraded yet. Data is upgraded daily in different intervals, 
so earlier in the morning the dataframe will be very sparse.
Don't panic. Just come back later in the day. Or check the source to see if there's 
an error there.""")  #poner text_area
	st.text_area('',"""There are some cases where China appears on the dataframe, although their 'oficial' numbers are not the highest of the top n.
		I still don't know why..""")
	#st.map(my_df)

	
	
	if st.button('Would you like to Dataframe as CSV?'):
	    if st.spinner('processing'):
	    	tmp_download_link = download_link(df, f'Top {n_countries}.csv', 'Click to download the data!')
	    	st.markdown(tmp_download_link, unsafe_allow_html=True)
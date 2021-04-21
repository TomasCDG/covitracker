import streamlit as st
import base64
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time


#my_bar = st.progress(0)
#for percent_complete in range(100):

st.set_page_config(page_title='CoviScaper',page_icon = ':mapamundi:', layout = 'centered')


st.title('Homemade Covid Tracker')
#st.header
st.subheader('Global Covid data updated from *Worldometers.info*')

st.markdown('**_Source_** : https://www.worldometers.info/coronavirus/')


#with st.spinner('Loading...'): #displays a temporary message 
#    time.sleep(2)
#    my_bar = st.progress(0)

############################################################################
############################################################################

def makesoup(url):
    ''' connect and get the soup from the page'''
    response = requests.get(url)
    soup= BeautifulSoup(response.content, "html.parser")
    return soup#.find_all('td')

def get_data(soup):
    return soup.find_all('td')

def get_country_names(soup):
    '''get all the names of the listed countries'''
    return [i.string for i in soup.find_all( style="font-weight: bold; font-size:15px; text-align:left;" )]

def get_country_indexes(countrylist):
    '''get the indexes where the countries are cited in the soup.
    This is done because we have no better insight of where to look at.
    So we use theese indexes and then parse their data in the next function'''
    indexes = {}
    for i in countrylist:
        indexes[i] = 'Notfound'

    countries_data = get_data(soup) 

    for i in countrylist:
        j=0
        while indexes[i] != 'NotFound' and j <= len(countries_data):
            if countries_data[j].string == i:
                indexes[i] = j
                break
            else:
                j+=1
    return indexes

def get_world_index():
    j=0
    x=get_data(soup)
    while x[j].string != 'World':
        j+=1
    else:
        return j

def get_pops(soup):
    pops = {}
    for i in get_data(soup):
        j = i.find('a', class_= '')
        if j != None:
            countryname = re.findall('population/(.+)-population/',str(j))
            #print(countryname[0],j.string)
            #number = int(str(j.string).replace(',',''))
            pops[countryname[0]] = j.string
    if 'us' in pops.keys(): 
        pops['usa'] = pops['us']
    return pops

def get_one_country_index(soup, country):
    j=0
    x=get_data(soup) #depreciated
    #x=soup
    while x[j].string != str(country):
        j+=1
    else:
        index = j
    return index

def get_country_data(soup , index):
    x=soup 
    x=get_data(soup) #depreciated
    data = x[index:index+15]
    
    
    data = [i.string for i in data] #.lstrip('+') #put every number as a string
    
    if data[0].lower() in get_pops(soup).keys():
        data[-2] =pops[data[0].string.lower()] #put the info about the total  population

    

    data[1:-1] = ['NA' if i == None or i ==  'N/A' or i.strip() == '' else i for i in data[1:-1]]
    data[1:-1] = [float(i.replace(',','')) if i != 'NA' else i for i in data[1:-1]] #I don't merge these two just in case some strange data appears
    
    return data

def df_top_countries(n):
    '''get the top n countries in terms of total cases'''
    
    cols = ['Country','Total Cases','New Cases','Total Deaths','New Deaths',
    'Total Recovered','New Recovered','Active Cases','Serious/Critical','TotalCases/1Mpop',
    'Deaths/1Mpop','Total Tests','Tests/1Mpop','Total pop','Region']
    
    stats = pd.DataFrame(get_country_data(soup,world_index), columns=['World'])
    
    for i in countries[0:n]:
    #print(get_country_data(soup,indexes[i]))
        stats[i] = get_country_data(soup,indexes[i])
    
    stats = stats.transpose()
    stats.columns = cols
    stats.set_index('Country',inplace=True)
    
    
    for i in stats.columns[0:-1]:
        stats[i] = stats[i].apply(lambda x : '{:,}'.format(int(x)) if x != 'NA' else x) #change into float if this fucks up
    
    return stats

def styler(df):
    
    return df.style.applymap(lambda x: 'background-color: indianred' if x =='NA' else  'background-color: snow',
              subset = df.columns[0:-1]).applymap(lambda x : 'background-color: palegreen'if x != 'NA' else 'background-color: maroon' , 
              subset = df.columns[0]).applymap(lambda x : 'background-color: lightgreen' if x == 'Asia' else 'background-color: skyblue' if x == 'North America' or x== 'South America'  else 'background-color: mediumslateblue' if x == 'Europe' else 'background-color: pink' if x == 'Africa' else x,
               subset = df.columns[-1])


def download_link(object_to_download, download_filename, download_link_text):
	object_to_download = object_to_download.to_csv(index=False)
	b64 = base64.b64encode(object_to_download.encode()).decode()
	return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

#def to_excel():
#	from openpyxl import Workbook
#	df.to_excel('covid.xlsx',sheet_name="Sheet1")
#	return 


if __name__ == "__main__":
	

	url = 'https://www.worldometers.info/coronavirus/'
	soup = makesoup(url)
	data = get_data(soup)
	my_bar.progress(25)

	countries = get_country_names(soup)
	indexes = get_country_indexes(countries)
	
	a='Select one country'
	b='See top countries by number of cases'
	options = st.radio('What would you like to see?' , (a, b))

	if options == a:

		st.text('in progress')
		
		sorted_countries = list(indexes.keys()) #to prevent any problem with the countries list
		sorted_countries.sort()
		chosen_country = st.selectbox('select the country you want to scrape', sorted_countries)
		#get_one_country_index(soup, country) to get one index only
		#get_country_data(soup,index_específico) to put this into df maker

	if options == b:
		
		st.subheader('please select how many countries with most cases you want to see. ')
		n_countries = st.number_input(label = "Top 'x' countries :", value= 10 , min_value =  1, max_value = len(countries))
		
		world_index = get_world_index()

		pops = get_pops(soup)
		df = df_top_countries(n_countries) #gets the country data

		styled_df = styler(df)
		st.dataframe(styled_df )
		st.write('_click on the uppper right of the table to maximize_')
		
		#st.table(styler(df)) way to laarge
		

		st.text_area('',"""Warning, some fields may be missing (NA), mostly the new cases, this is because the
corresponding data has not been upgraded yet. Data is upgraded daily in different intervals, 
so earlier in the morning the dataframe will be very sparse.
Don't panic. Just come back later in the day. Or check the source to see if there's 
an error there.""")  #poner text_area

		#st.map(my_df)

		
		
		if st.button('Would you like to Dataframe as CSV?'):
		    if st.spinner('processing'):
		    	tmp_download_link = download_link(df, f'Top {n_countries}.csv', 'Click to download the data!')
		    	st.markdown(tmp_download_link, unsafe_allow_html=True)
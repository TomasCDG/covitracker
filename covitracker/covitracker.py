import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np

'''
1. makesoup calls the page and .. makes the soup
2. get_data gets all the <td> elements that contain our desired data
##########################
#### We can't make a finer and more precise selection than that, as the table on the webpage is structured in a way that makes it terribly difficult to scrape precisely.
#### It is because of that that we need to iterate over the list of <td>s to find every country name, their stats, and so on.
###########################

3. get_country names iterates over the soup to find the country names, looking for a fixed separation of lines between the names.
4. get_country_indexes looks for the position of ALL these names in the soup. the indexes
		Then, we get a nice dictionary with all the countries' names and their positions on the soup.
		This way, we can scrape selectively over this long list by iteration, not by precise scraping.

5. get_world_index looks for the index of the world's total stats.

6. get_pops iterates over the soup to find (unindex and unreferenced) the total population of every country


7. get_one_country_index looks for the index in which a specific country's data begins to appear, taken 
8. get_country_data looks takes that last index and scrapes the data's information.
9. df_country gets me a small dataframe with the selected country's stats. 

10. df_top_countries gets me a df with the top N countries and their stats. The 'top' countries are the ones with most cases.
11. styler just returns the same df but with some highlighted colors.

12. download_link let's me download the dataframe into a csv file.

'''



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



def get_country_indexes(soup, countrylist):
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



def get_world_index(soup):
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



def get_country_data(soup , index ,pops ):
    x=soup 
    x=get_data(soup) #depreciated

    data = x[index:index+15]
    
    
    data = [i.string for i in data] #.lstrip('+') #put every number as a string
    
    if data[0].lower() in get_pops(soup).keys():
        data[-2] =pops[data[0].string.lower()] #put the info about the total  population

    

    data[1:-1] = ['NA' if i == None or i ==  'N/A' or i.strip() == '' else i for i in data[1:-1]]
    data[1:-1] = [float(i.replace(',','')) if i != 'NA' else i for i in data[1:-1]] #I don't merge these two just in case some strange data appears
    
    return data



def df_country(soup, chosen_country, indexes):
    country_index = get_one_country_index(soup, chosen_country)
    pops = get_pops(soup)
    series = get_country_data(soup,country_index,pops)
    
    index = ['Country','Total Cases','New Cases','Total Deaths','New Deaths',
    'Total Recovered','New Recovered','Active Cases','Serious/Critical','TotalCases/1Mpop',
    'Deaths/1Mpop','Total Tests','Tests/1Mpop','Total pop','Region']
    
    return pd.DataFrame(series, index = index, columns = ['stats'])



def df_top_countries(soup,n):
    '''get the top n countries in terms of total cases'''
    
    cols = ['Country','Total Cases','New Cases','Total Deaths','New Deaths',
    'Total Recovered','New Recovered','Active Cases','Serious/Critical','TotalCases/1Mpop',
    'Deaths/1Mpop','Total Tests','Tests/1Mpop','Total pop','Region']
    pops = get_pops(soup)
    world_index = get_world_index(soup)
    stats = pd.DataFrame(get_country_data(soup,world_index,pops), columns=['World'])
    

    countries = get_country_names(soup)
    indexes = get_country_indexes(soup, countries)
    for i in countries[0:n]:
    #print(get_country_data(soup,indexes[i]))
        stats[i] = get_country_data(soup,indexes[i],pops)
    
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

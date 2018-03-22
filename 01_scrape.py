import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np 
import re


### Config
import api_keys




### Scrape Table
wiki = requests.get('https://en.wikipedia.org/wiki/List_of_diplomatic_missions_in_Washington,_D.C.')
soup = BeautifulSoup(wiki.content, 'html.parser')
#print(soup.prettify)



### Table Data
table = soup.find('table', class_="wikitable")

col_names = [item.get_text() for item in table.find_all('th')]
table_data = [item.get_text() for item in table.find_all('td')]
rows = int(len(table_data)/len(col_names))
cols = len(col_names)
data = np.reshape(table_data, (rows, cols))



### Images
image_urls = [item.get('src') for item in table.find_all('img')]
# Some table entries are missing images of the embassy--insert blanks to maintain table shape
missing_image_index = []
for i in range(rows * 2 - 1):
    j = i + 1
    if re.match('.*Flag.*', image_urls[i]) and re.match('.*Flag.*', image_urls[j]):
        image_urls.insert(j, '')
        missing_image_index.append(j)
        
if len(image_urls) % 2 != 0: image_urls.append('')

data = np.append(data, np.reshape(image_urls, (rows, 2)), axis=1)
col_names.append('Flag_url')
col_names.append('Image_url')

image_heights = [item.get('height') for item in table.find_all('img')]
image_widths = [item.get('width') for item in table.find_all('img')]

for i in missing_image_index:
    image_heights.insert(i, '0')
    image_widths.insert(i, '0')
    
data = np.append(data, np.reshape(image_heights, (rows, 2)), axis=1)
data = np.append(data, np.reshape(image_widths, (rows, 2)), axis=1)

col_names.append('Flag_height')
col_names.append('Image_height')
col_names.append('Flag_width')
col_names.append('Image_width')



### Referances
ref_id = []
ref_url = []
for item in soup.find_all(id=re.compile('cite_note-[0-9]+')):
    ref_id.append(item.get('id'))
    ref_url.append(item.find(class_=('external text', 'external free')).get('href'))
    
ref_df = pd.DataFrame({'Reference_id': ref_id, 'Reference_url': ref_url})
ref_df['Reference_id'].replace('cite_note-', '', regex=True, inplace=True) 
ref_df.set_index(ref_df['Reference_id'], inplace=True)



### Into Dataframe
df = pd.DataFrame(data = data, columns=col_names)

df['Notes'].replace('[\[\]]', '', regex=True, inplace=True)
df = df.join(ref_df['Reference_url'], on='Notes')

# Clean Up
df['Embassy'].replace('\\n38.*', '', regex=True, inplace=True)
df['Neighborhood'].replace('\\n38.*', '', regex=True, inplace=True)
df['Location'].replace('\\n38.*', '', regex=True, inplace=True)
df['Location_query'] = df['Location'].apply(lambda x: x + ', Washington, DC')
df['Flag_url'] = df['Flag_url'].apply(lambda x: 'https:' + x)
df['Image_url'] = df['Image_url'].apply(lambda x: 'https:' + x)



### Get Coordinates
def coordinates(address, api_key):
    # https://github.com/ffreitasalves/python-address-to-coordinates/blob/master/script.py
    url = 'https://maps.googleapis.com/maps/api/geocode/json'

    params = {'address': address.encode('ascii', 'xmlcharrefreplace'), 
              'sensor': 'false', 
              'key': api_key}

    response = requests.get(url, params=params)
    coord = response.json()

    if coord['status']=='OVER_QUERY_LIMIT':
        raise RuntimeError(coord['error_message'])

    if coord['status']=='OK':
        return {'lat': coord['results'][0]['geometry']['location']['lat'],
                'lng': coord['results'][0]['geometry']['location']['lng']}
    else:
        return {'lat': '', 'lng': ''}


df['lat'] = ''
df['lng'] = ''
for i in range(len(df.index)):
    coord = coordinates(df['Location_query'][i], api_keys.google)
    df['lat'][i] = coord['lat']
    df['lng'][i] = coord['lng']



### Save Data
df.to_csv("embassy_locations.csv", index=False)



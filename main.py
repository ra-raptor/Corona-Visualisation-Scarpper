#imports
import requests,os,folium,time,base64
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from folium import IFrame
from bs4 import BeautifulSoup
#resources
directory = os.path.dirname(__file__)
figFile = os.path.join(directory,'Figure')
BorderData = os.path.join(directory,'mapData/states.json')
WikkiURL = "https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_India"
#creating a coordinate system dataframe for all states in india
All_states = ['Andhra Pradesh','Bihar','Chandigarh','Chhattisgarh','Delhi','Gujarat','Haryana','Himachal Pradesh','Jammu and Kashmir','Karnataka','Kerala','Madhya Pradesh','Maharashtra','Odisha','Puducherry','Punjab','Rajasthan','Tamil Nadu','Telangana','Uttarakhand','Uttar Pradesh','West Bengal','Arunachal Pradesh','Assam','Goa','Jharkhand','Manipur','Meghalaya','Mizoram','Nagaland','Sikkim','Tripura','Andaman and Nicobar Islands','Lakshadweep','Dadra and Nagar Haveli and Daman and Diu']
ll_cap_coord = [ [14.7504291,78.57002559], [25.78541445,87.4799727],  [30.71999697,76.78000565], [22.09042035,82.15998734],[28.6699929,77.23000403],[22.2587,71.1924],  [28.45000633,77.01999101], [31.10002545,77.16659704],    [34.29995933,74.46665849],  [12.57038129,76.91999711], [8.900372741,76.56999263],  [21.30039105,76.13001949],   [19.25023195,73.16017493],  [19.82042971,85.90001746],[11.93499371,79.83000037],[31.51997398,75.98000281],[26.44999921,74.63998124],[12.92038576,79.15004187], [18.1124, 79.0193],[30.32040895,78.05000565],[27.59998069,78.05000565], [22.58039044,88.32994665], [27.10039878,93.61660071],[26.7499809,94.21666744],[15.491997,73.81800065],[23.80039349,86.41998572],[24.79997072,93.95001705], [25.57049217,91.8800142], [23.71039899,92.72001461],[25.6669979,94.11657019],[27.3333303,88.6166475],[23.83540428,91.27999914],[11.66702557,92.73598262], [10.56257331,72.63686717],[20.26657819,73.0166178]]
temp = {
    'states' : All_states,
    'Coordinates' : ll_cap_coord
}
Coord = pd.DataFrame(temp)
#scraping data
print('Scrapping Wikki')
response = requests.get(WikkiURL,stream=True)
total_size = int(response.headers.get('content-length',0))
print('Size : ',total_size,' bytes')
soup = BeautifulSoup(response.text,'html.parser')
#wikkiedia changed its table structure so class was changed (25 March 2020)
table = soup.find('table',{'class':"wikitable mw-collapsible mw-collapsed"}).tbody
#table = soup.find('table',{'class':"wikitable mw-collapsible mw-made-collapsible"}).tbody
rows = table.find_all('tr')
column_name = [v.text.replace('\n','') for v in rows[1].find_all('th')]
column_name.pop()
column_name.pop()
column_name.pop()
column_name.pop()
column_name.insert(0,'Date')
print(column_name)
#creating dataframe for data about per day Confirmation in each state
df = pd.DataFrame(columns=column_name)
for i in range(1,len(rows)):
    tds = rows[i].find_all('td')
#initially : value = [tds[x].text.replace('\n','') for x in range(0,len(tds)-5)] 
#wikkipedia changed table structure so code was updated on (25 march 2020)
    value = [tds[x].text.replace('\n','') for x in range(0,len(tds)-6)] 

    for y in range(len(value)):
        if '(' in value[y]:
            value[y] = value[y][:-3]

    for i in range(0,len(value)):
        if value[i] == '':
            value[i] = 0
    
    if len(value) >= 23:
        df = df.append(pd.Series(value,index=column_name),ignore_index=True)
df.to_csv('data.csv',index=False)
print(df)
print('waiting...')
time.sleep(1)
df.fillna(0,inplace=True)
df.reindex()
a= df.copy()
a = a.drop('Date',1)
#graph stuff
dates = np.array(df.Date)
def ToINT(arr):
    x = []
    for i in arr:
        x.append(int(i))
    return(x)

def CumSum(arr):
    new = []
    cums = 0
    for element in arr:
        cums += element
        new.append(cums)
    return(new)

def MakeGraph(data,titl):
    a = ToINT(data)
    b = CumSum(a)
    c = np.array(b)
    plt.plot(dates,c,color='red')
    plt.xlabel('Date')
    plt.ylabel('Confirmed Cases')
    plt.title(titl)
    plt.xticks(rotation=90)
    #plt.show()
    n = titl+'.png'
    name = os.path.join(figFile,n)
    #print('saving Images',n)
    plt.savefig(name,bbox_inches = 'tight', pad_inches=.1,quality=40,)
    plt.close()

for (columnName,columnData) in a.iteritems():
    if columnName != 'Date':
        MakeGraph(a[columnName],columnName)

#overAll data for showing as a msak in the map
value_overall = rows[-4].find_all('th')
value_overall_data = []
b = [int(value_overall[x].text.replace('\n','')) for x in range(1,len(value_overall)-5)]
value_overall_data.extend(b)
overall_index = column_name
overall_index.remove('Date')
data = {
    'state' : overall_index,
    'cases' : value_overall_data
}
overall = pd.DataFrame(data)
print(overall)

#removing markers from those states still not infected
for state in All_states:
    if state not in overall_index:
        Coord = Coord[Coord.states != state]

#creating map
m = folium.Map(tiles='OpenStreetMap',zoom_start=5,location=[23.7957, 86.4304],min_zoom=4,max_zoom=7,min_lat=0,max_lat=40,min_lon=70,max_lon=100)

for (index,row) in Coord.iterrows():
    name = row.loc['states']
    filename = row.loc['states']+'.png'
    location = os.path.join(figFile,filename)
    encoded = base64.b64encode(open(location, 'rb').read())
    html = '<img src="data:image/png;base64,{}">'.format
    pic = base64.b64encode(open(location,'rb').read()).decode()
    iframe = IFrame(html(pic),width=700+20,height=500+20)
    #iframe = folium.IFrame(html(encoded.decode('UTF-8')), width=(100*300)+20, height=(100*300)+20)
    popup = folium.Popup(iframe,max_width=650)
    folium.Marker(row.loc['Coordinates'],tooltip=row.loc['states'],popup=popup,icon=folium.Icon(color='red',icon='glyphicon glyphicon-warning-sign')).add_to(m)





#folium.Marker([14.7504291,78.57002559],popup="AP",tooltip='click',icon=logoIcon).add_to(m)
m.choropleth(
    geo_data= BorderData,
    name='choropleth',
    data=overall,
    columns=['state','cases'],
    key_on='feature.properties.NAME_1',
    fill_color='OrRd',
    fill_opacity=0.9,
    line_opacity=0.2,
    legend_name='Confirmed',
    nan_fill_color='#14e83b',
    nan_fill_opacity=0.9
)

folium.LayerControl().add_to(m)
m.save('index.html')



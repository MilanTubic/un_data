import requests
import csv
import json
import sqlite3
import pandas as pd
import random
from pprint import pprint
from itertools import cycle
from bs4 import BeautifulSoup


ComtradeApi_url = 'http://comtrade.un.org/api/get?'


def to_csv() :
    db = sqlite3.connect('test.db')
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table_name in tables :
        table_name = table_name[0]
        table = pd.read_sql_query("SELECT Country, Yr, TradeValue, rgDesc from %s" % table_name, db)
        with open('out.csv', 'a') as f :
            table.to_csv(f, header=f.tell() == 0)

    cursor.close()
    db.close()

   # Mannually load working proxy list
# def get_proxies() :
#     with open('proxy.csv') as csvfile1 :
#         reader1 = csv.DictReader(csvfile1)
#         proxies = set()
#         for row in reader1 :
#             # Grabbing IP and corresponding PORT
#             proxy = row['Prox']
#             proxies.add(proxy)
#     return proxies

   # Get proxy list from net
res = requests.get('https://free-proxy-list.net/', headers={'User-Agent':'Mozilla/5.0'})
soup = BeautifulSoup(res.text,"lxml")
proxy_l=[]
for items in soup.select("#proxylisttable tbody tr"):
    proxy_list = ':'.join([item.text for item in items.select("td")[:2]])
    proxy_l.append(proxy_list)
proxies = proxy_l
random.shuffle(proxies)

  #Set proxy cycle
proxy_pool = cycle(proxies)
proksi = next(proxy_pool)
print(proksi)


  #Load countries
countrylist = []
with open('un_country_code_list.csv') as csvfile :
    reader = csv.DictReader(csvfile)
    c=0
    for row in reader :
        CountryCode = row['Country Code']
        CountryName = row['ISO3-digit Alpha']
        if CountryName != 'N/A': countrylist.insert(c,(CountryCode,str(CountryName)))
        c +=1

print(countrylist)

conn = sqlite3.connect('test.db')
curs = conn.cursor()

   #start loop for all countries
for it in range(1,len(countrylist)):

        curr_country = countrylist[it][0]
        country_name = str(countrylist[it][1])

        print(country_name)
        country_n=str(country_name+'_'+curr_country)

        con1 = ("""CREATE TABLE IF NOT EXISTS
         %s (Country, Yr, Period, Month, TradeValue, TradeDescE, rgDesc, Code, PartnerCode); """ % country_n)
        curs.execute(con1)


        n = 'all'   #var for Year value, can be set to specific year or iter for range.

        im=0  #im switch

        url1 = str(ComtradeApi_url) + 'max=500&type=C&freq=Y&px=HS&ps=' + str(n) + '&r=' + (
        curr_country) + '&p=0&rg=all&cc=TOTAL'
        print(url1)
        while im == 0:
            try:
                r = requests.get(url1, proxies={"https" : proksi, "http" : proksi})
                # r = requests.get(url1)

                i=0  #set i switch in order to try all proxies
                while r.status_code != 200 and i < 2*len(proxies):
                    try:
                        print('no server responce')
                        proksi = next(proxy_pool)
                        print(proksi)
                        # r = requests.get(url1)
                        r = requests.get(url1, proxies={"https" : proksi, "http" : proksi})

                    except Exception as e:
                        print(e)
                        proksi = next(proxy_pool)
                        i += 1

                else:
                    try:
                        cont = json.loads(r.content.decode())
                        im = 1 #set im switch after server response
                        pprint(r.content.decode())
                        sqlite_insert = ("""INSERT INTO %s
                                               (Country, Yr, Period, Month, TradeValue, TradeDescE, rgDesc, Code, PartnerCode) 
                                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);""" % country_n)
                        for item in cont['dataset']:
                            Yr = item['yr']
                            Period = item['period']
                            Month = item['periodDesc']
                            TradeValue = item['TradeValue']
                            print(TradeValue)
                            TradeDescE = item['cmdDescE']
                            rgDesc = item['rgDesc']
                            Code = item['rtCode']
                            PartnerCode = item['ptCode']
                            data_tuple = (country_name, Yr, Period, Month, TradeValue, TradeDescE, rgDesc, Code, PartnerCode)
                            curs.execute(sqlite_insert, data_tuple)
                            conn.commit()
                            data_tuple = ()
                        print(im)

                    except Exception as e:
                        print(e)
                        proksi = next(proxy_pool)
                        im=0

            except Exception as e:
               print(e)
               proksi = next(proxy_pool)
               im=0

        #sleep(randint(6, 10))


        # end loop for url

# end loop for countries
curs.close()
conn.close()

to_csv() #export to csv


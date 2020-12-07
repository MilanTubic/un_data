import concurrent.futures
from bs4 import BeautifulSoup
import requests
import time


def funkcija(prox):
    urlpr = str("http://google.com")
    start=time.perf_counter()
    while round(time.perf_counter() - start) < 1 :
      try :
          r = requests.get(urlpr, proxies={"https" : prox, "http" : prox})

          if r.status_code == 200 :
              print(prox)
              return prox
              break

      except Exception as e :
            print("next")
            break



res =requests.get('https://free-proxy-list.net/', headers={'User-Agent' : 'Mozilla/5.0'})
soup = BeautifulSoup(res.text, "lxml")

proxy_l = []
for items in soup.select("#proxylisttable tbody tr"):
    proxy_list = ':'.join([item.text for item in items.select("td")[:2]])
    proxy_l.append(proxy_list)

print(proxy_l)

proxy_ok=[]
# try :
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = []
    for item in proxy_l:
         futures.append(executor.submit(funkcija,prox=item))
    try :

        for future in concurrent.futures.as_completed(futures) :
            if future.result()!= None:
                proxy_ok.append(future.result())
    except Exception as e :
        print(e)

print(proxy_ok)

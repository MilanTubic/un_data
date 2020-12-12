#import concurrent.futures
import concurrent.futures.thread
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
import requests
from requests.exceptions import HTTPError
import time

import multiprocessing



def funk(prox) :
    #  urlpr = str("http://google.com")
    start = time.perf_counter()
    try :
        r = requests.get("http://google.com", timeout=14, proxies={"http" : prox,"https" : prox })
        t1 = time.perf_counter() - start
        if r.status_code == 200 and t1 < 14 :
            print(prox + " responded in " + str(round(t1, 2)) + " seconds")

            return prox
            r.close()

    except HTTPError as http_err :
        print(http_err)
        pass

    except Exception as err :
        print(err)
        pass


res = requests.get('https://free-proxy-list.net/', headers={'User-Agent' : 'Mozilla/5.0'})
soup = BeautifulSoup(res.text, "lxml")

proxy_l = []
for items in soup.select("#proxylisttable tbody tr") :
    proxy_list = ':'.join([item.text for item in items.select("td")[:2]])
    proxy_l.append(proxy_list)

print(proxy_l)

proxy_ok = []
# try :
long = 0
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = []

    start = time.perf_counter()
    futures = [executor.submit(funk, p) for p in proxy_l]

    try :
        for future in as_completed(futures):

            if future.result() != None :
                proxy_ok.append(future.result())
                long = len(proxy_ok)
                print('Found '+str(long)+' working proxies.')
            if long >= 10:
                executor._threads.clear()
                concurrent.futures.thread._threads_queues.clear()
                break

    except Exception as err :
        print(err)
        pass

    finally :
        executor.shutdown()

print(proxy_ok)

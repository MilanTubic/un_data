import concurrent.futures
from bs4 import BeautifulSoup
import requests
import time


def funkcija(prox):
    urlpr = str("http://comtrade.un.org")
    start = time.perf_counter()

    try:
        r = requests.get(urlpr,timeout=14, proxies={"https": prox, "http": prox})
        t1 = time.perf_counter() - start
        if r.status_code == 200 and t1<14:
            print(prox+" responded in "+str(t1)+" seconds")
            r.connection.close()
            return prox

    except Exception:
        print("next")



res = requests.get('https://free-proxy-list.net/',headers={'User-Agent':'Mozilla/5.0'})
soup = BeautifulSoup(res.text, "lxml")

proxy_l = []
for items in soup.select("#proxylisttable tbody tr"):
    proxy_list = ':'.join([item.text for item in items.select("td")[:2]])
    proxy_l.append(proxy_list)

print(proxy_l)

proxy_ok=[]


with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
    futures = []
    start = time.perf_counter()
    futures = [executor.submit(funkcija, p) for p in proxy_l]
    try :
        for future in concurrent.futures.as_completed(futures, timeout=300):

            if future.result() is not None:
                proxy_ok.append(future.result())

    except concurrent.futures.TimeoutError:
        print("This took to long...")


    finally :
        executor.shutdown()


print(proxy_ok)

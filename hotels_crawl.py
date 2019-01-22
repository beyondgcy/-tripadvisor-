from os.path import isfile
import sqlite3
import requests
from bs4 import BeautifulSoup
import re
import os, time
import random


#页面信息请求函数
def load_soup_online(url):
    try:
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'
        headers = {'User-Agent': user_agent}
        req = requests.get(url,headers=headers)
        data = req.text
        req.close()
        return BeautifulSoup(data, 'lxml')
    except:
        print("Connection refused by the server..")
        print("Let me sleep for 5 seconds")
        print("ZZzzzz...")
        time.sleep(random.uniform(1, 10))
        print("Was a nice sleep, now let me continue...")
        data = load_soup_online(url)
        return data

#找每个页面的链接,以列表形式返回
def find_page_urls(url):
    soup_container = load_soup_online(url)
    div = soup_container.find('div', class_='pageNumbers')
    if div is None:
        return 1
    else:
        # 以列表形式返回<a class="pageNum last taLnk "开头的所有链接，取最后一个
        num = div.find_all('a')[-1]
        # 返回data-page-number对应的字段
    page_num = int(num['data-page-number'])
    page_urls=[url]
    url_start = re.search('.+\d+', url, re.M | re.I)
    for i in range(1,page_num):
        page_url = re.sub('.+\d+', url_start.group()+'-oa'+str(i*30), url)
        page_urls.append(page_url)
    return page_urls

#找所有宾馆的链接,传入参数为页面列表
def find_hotel_urls(urls):
    all_hotel_urls = []
    for url in urls:
        soup_container = load_soup_online(url)
        hdr = soup_container.find_all('div', class_='listing_title')
        for link in hdr:
            pair_url = link.a.attrs['href']
            all_hotel_urls.append('https://www.tripadvisor.com/' + pair_url[1:])
    # 去掉重复的宾馆链接
    hotel_urls = []
    for hotel_url in all_hotel_urls:
        if hotel_url in hotel_urls:
            pass
        else:
            hotel_urls.append(hotel_url)
    return hotel_urls

#使用时修改init_urls,替换为新链接
# init_urls = ['https://www.tripadvisor.com/Hotels-g60491-Jackson_Jackson_Hole_Wyoming-Hotels.html']
init_urls = []
with open('城市链接.txt', "r") as files:
    for line in files.readlines():
        line = line.strip('\n')
        line = line.strip('\'')
        init_urls.append(line)
print(init_urls)
if __name__ == '__main__':
    for city_url in init_urls:
        code = re.findall('\d+', city_url)
        cityCode = code[0]
        #找出当前城市名称
        city = re.findall('(?<=\d-).*?(?=-)', city_url)
        hotelCity = city[0]
        print('I am crawling this city:'+hotelCity+' '+str(cityCode))
        page_urls = find_page_urls(city_url)
        print('这个城市的所有宾馆页面列表如下：')
        print(page_urls)
        hotel_urls = find_hotel_urls(page_urls)
        print('这个城市的所有宾馆列表如下：')
        print(hotel_urls)
        print(len(hotel_urls))
        fn = hotelCity + '_hotels.txt'
        with open(fn, "w") as f:
            for url in hotel_urls:
                f.write(url)
                f.write('\n')
        hotels = []
        with open(fn, "r") as file:
            for line in file.readlines():
                line = line.strip('\n')
                hotels.append(line)
        print(hotels)

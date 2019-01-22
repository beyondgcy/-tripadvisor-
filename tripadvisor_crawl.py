from os.path import isfile
import sqlite3
import requests
from bs4 import BeautifulSoup
import re
import os, time
import random
import math
import csv
import datetime
from collections import Counter


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
def load_soup(url):
    try:
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'
        headers = {'User-Agent': user_agent}
        req = requests.get(url, headers=headers)
        data = req.text
        req.close()
        return BeautifulSoup(data, 'lxml')
    except:
        return ''

def load_soup_review(id):
    try:
        base_url = 'https://www.tripadvisor.com/OverlayWidgetAjax'
        params = {'Mode':'EXPANDED_HOTEL_REVIEWS',
                'metaReferer':'Restaurant_Review',
                'reviews':id}
        headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'}
        req = requests.get(base_url,params=params,headers=headers)
        data = req.text
        req.close()
        return BeautifulSoup(data, 'html.parser')
    except:
        print("Connection refused by the server..")
        print("Let me sleep for 5 seconds")
        print("ZZzzzz...")
        time.sleep(random.uniform(1, 10))
        print("Was a nice sleep, now let me continue...")
        data = load_soup_review(id)
        return data
def load_soup_contributor(uid,src):
    try:
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'}
        user_info_url = 'https://www.tripadvisor.com/MemberOverlay?Mode=owa&uid={uid}&c=&src={src}&fus=false&partner=false&LsoId=&metaReferer=ShowUserReviewsHotels'
        url = user_info_url.format(uid=uid,src=src)
        resp = requests.get(url,headers=headers)
        resp.close()
        html = resp.text
        return BeautifulSoup(html, 'html.parser')
    except:
        print("Connection refused by the server..")
        print("Let me sleep for 5 seconds")
        print("ZZzzzz...")
        time.sleep(random.uniform(1, 10))
        print("Was a nice sleep, now let me continue...")
        data = load_soup_contributor(uid,src)
        return data
#评论动态页面请求函数
def load_soup_reviews(url):
    try:
        data = {'preferFriendReviews': 'FALSE',
                'filterSeasons': '',
                'filterLang': 'ALL',  #
                'reqNum': 1,
                'isLastPoll': 'false',
                # 'paramSeqId': 1,
                'changeSet': 'REVIEW_LIST',
                # 'puid': 'W@q@6AoQI4UAALjdO38AAABN'
                }  # puid
        headers = {
            'referer': 'https://www.tripadvisor.com/Hotel_Review-g60491-d101222-Reviews-Super_8_by_Wyndham_Jackson_Hole-Jackson_Jackson_Hole_Wyoming.html',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Safari/605.1.15',
            'x-requested-with': 'XMLHttpRequest'}
        req = requests.post(url, data=data, headers=headers)
        data = req.content
        req.close()
        return BeautifulSoup(data, 'html.parser')
    except:
        print("Connection refused by the server..")
        print("Let me sleep for 5 seconds")
        print("ZZzzzz...")
        time.sleep(random.uniform(1, 10))
        print("Was a nice sleep, now let me continue...")
        data = load_soup_reviews(url)
        return data


#找出hotel的相关信息，返回
def find_hotel_page_data(url):
    #找出评论数目
    soup_container = load_soup_online(url)
    # 利用location的信息进行循环，确保请求有值
    while 'ui_columns is-multiline is-mobile contentWrapper' not in str(soup_container):
        soup_container = load_soup_online(url)
    # print(soup_container)
    #找出题目的源码
    description = soup_container.find('div', class_='ui_columns is-multiline is-mobile contentWrapper')
    hdr = description.find('span', class_='reviewCount')
    if hdr == None:
        review_num = 0
    else:
        textObj = re.sub(',', '', hdr.text)
        text = re.search('\d+', textObj)
        review_num = int(text.group())
    # 找出评论页面，每5个一个
    url_start = re.search('.+Reviews', url)
    review_page_urls = []
    review_page_urls.append(url)
    for n in range(1, math.ceil(review_num / 5)):
        review_page_url = re.sub('.+Reviews', url_start.group() + '-or' + str(n * 5), url)
        review_page_urls.append(review_page_url)
    #找出市内排名
    try:
        rank = description.find('div', class_='prw_rup prw_common_header_pop_index popIndex')
        rank_b = rank.find('b')
        rank_of = re.search(' of \d+ ', str(rank))
        rank_a = rank.find('a')
        hotelRankInCity = rank_b.text + rank_of.group() + rank_a.text
    except:
        hotelRankInCity = None
    #找出总体评级
    rating = description.find('div', class_='prw_rup prw_common_bubble_rating rating')
    ratingObj = re.search('(?<=span alt=").*(?= of 5 bubbles)', str(rating))
    try:
        hotelOverallRating = ratingObj.group()
    except:
        hotelOverallRating=None
    #找出地址
    address1 = description.find('span', class_='street-address')
    address2 = description.find('span', class_='locality')
    hotelAddress = re.sub('<.*?>','',str(address1))+re.sub('<.*?>','',str(address2))
    # 利用location的信息进行循环，确保请求有值
    while '<div class="sub_title">Location</div>' not in str(soup_container):
        soup_container = load_soup_online(url)
    # print(soup_container)
    # 找出全部信息字段
    Aboutinfo = soup_container.find('div', id='ABOUT_TAB')
    Allinfo = Aboutinfo.find('div', class_='ui_column is-3 is-shown-at-desktop')
    while Allinfo == None:
        soup_container = load_soup_online(url)
        Aboutinfo = soup_container.find('div', id='ABOUT_TAB')
        Allinfo = Aboutinfo.find('div', class_='ui_column is-3 is-shown-at-desktop')
    # 地点
    hotelLocation = None
    while hotelLocation == None:
        try:
            locationObj = re.search('(?<=Location</div><div class="sub_content"><div class="textitem" data-prwidget-init="" data-prwidget-name="text">).*?(?=</div>)',str(Allinfo))
            hotelLocation = locationObj.group()
            hotelLocation = re.sub(' &gt; ', '>', hotelLocation)
        except:
            hotelLocation = None
    #酒店星级
    try:
        star = soup_container.find('div', class_='prw_rup prw_common_star_rating')
        starObj = re.search('(?<=ui_star_rating star_)\d+', str(star))
        hotelClass = starObj.group()[0]+'.'+starObj.group()[1]
    except:
        hotelClass = None
    #奖项与认证
    badgesObj = soup_container.find('div', class_='sub_content badges is-shown-at-desktop')
    badges = re.findall('(?<=<span class="ui_icon ).*?(?=</span>)',str(badgesObj))
    # print(badges)
    for badge in badges:
        badges[badges.index(badge)] = re.sub('.*>','',badge)
    a = ', '
    hotelAwards = a.join(badges)
    try:
        if badgesObj.find('span', class_='award_text') != None:
            s = badgesObj.find('span', class_='award_text')
            hotelAwards = s.text + hotelAwards
    except:
        pass
    #宾馆风格
    try:
        styleObj = Allinfo.find_all('div',class_='textitem style')
        styles = []
        for style in styleObj:
            styles.append(style.text)
        b=','
        hotelStyle = b.join(styles)
    except:
        hotelStyle = None
    #房间风格
    try:
        typesObj = re.search('(?<=Room types</div><div class="sub_content"><div class="textitem" data-prwidget-init="" data-prwidget-name="text">).*?(?=</div>)',str(Allinfo))
        hotelRoomTypes = typesObj.group()
    except:
        hotelRoomTypes = None
    #房间数量
    try:
        numObj = re.search('(?<=Number of rooms</div><div class="sub_content"><div class="textitem" data-prwidget-init="" data-prwidget-name="text">).*?(?=</div>)',str(Allinfo))
        hotelRoomNum = numObj.group()
    except:
        hotelRoomNum = None
    #价格区间
    try:
        rangeObj = re.search('(?<=Price range</div><div class="sub_content"><div class="textitem" data-prwidget-init="" data-prwidget-name="text">).*?(?=</div>)',str(Allinfo))
        hotelPriceRange = rangeObj.group()
    except:
        hotelPriceRange = None
    reviewDistribution = load_soup_reviews(url)
    distribution = reviewDistribution.find_all('span',class_="row_num is-shown-at-tablet")
    maxTimes = 5
    while distribution == [] and maxTimes != 0:
        reviewDistribution = load_soup_reviews(url)
        distribution = reviewDistribution.find_all('span',class_="row_num is-shown-at-tablet")
        maxTimes -= 1
    if distribution == []:
        hotelRatingExcellent = hotelRatingVeryGood = hotelRatingAverage = hotelRatingPoor = hotelRatingTerrible =0
    else:
        hotelRatingExcellent = re.sub(',','',distribution[0].text)
        hotelRatingVeryGood = re.sub(',','',distribution[1].text)
        hotelRatingAverage = re.sub(',','',distribution[2].text)
        hotelRatingPoor = re.sub(',','',distribution[3].text)
        hotelRatingTerrible = re.sub(',','',distribution[4].text)

    return review_page_urls,review_num,hotelRankInCity,hotelOverallRating,hotelAddress,hotelClass,\
           hotelAwards,hotelStyle,hotelRoomTypes,hotelRoomNum,hotelPriceRange,hotelLocation,\
           hotelRatingExcellent, hotelRatingVeryGood, hotelRatingAverage, hotelRatingPoor, hotelRatingTerrible


def find_review_urls(page_urls):
    list = []
    for url in page_urls:
        if page_urls.index(url) % 10 == 0:
            print('%.2f'%(100*page_urls.index(url)/len(page_urls)),end='')
            print('% ')
        soup_container = load_soup_reviews(url)
        review = soup_container.find_all('div', class_='quote')
        maxTimes = 5
        while review==[] and maxTimes!=0:
            soup_container = load_soup_reviews(url)
            review = soup_container.find_all('div', class_='quote')
            maxTimes -= 1
        for quote in review:
            reviewObj = re.search('/ShowUserReviews.+html', str(quote), re.M | re.I)
            review_url = 'https://www.tripadvisor.com' + reviewObj.group()
            list.append(review_url)
    return list

#使用时修改init_urls,替换为新链接
# init_urls = ['https://www.tripadvisor.com/Hotels-g60491-Jackson_Jackson_Hole_Wyoming-Hotels.html']
# init_urls = ['https://www.tripadvisor.com/Hotels-g31352-Sedona_Arizona-Hotels.html']
init_urls = ['https://www.tripadvisor.com/Hotels-g4237367-Four_Corners_Florida-Hotels.html']
if __name__ == '__main__':
    starttime = datetime.datetime.now()
    for city_url in init_urls:
        code = re.findall('\d+', city_url)
        cityCode = code[0]
        #找出当前城市名称
        city = re.findall('(?<=\d-).*?(?=-)', city_url)
        hotelCity = city[0]
        print('I am crawling this city:'+hotelCity+' '+str(cityCode))
        fn = hotelCity+'.csv'
        if not isfile(fn):
            csvfile = open(fn, 'a+', encoding='utf-8', newline='')
            writer = csv.writer(csvfile)
            writer.writerow(('cityCode','hotelURL', 'hotelCode', 'hotelCity', 'cityHotelNum', 'hotelRankInCity',
                             'hotelName', 'hotelReviewNum', 'hotelOverallRating', 'hotelAddress', 'hotelClass',
                             'hotelAwards', 'hotelStyle', 'hotelRoomTypes', 'hotelRoomNum', 'hotelPriceRange',
                             'hotelLocation', 'hotelReviewNum', 'hotelRatingExcellent', 'hotelRatingVeryGood',
                             'hotelRatingAverage',
                             'hotelRatingPoor', 'hotelRatingTerrible', 'reviewURL', 'reviewTool', 'reviewRating',
                             'reviewTitle',
                             'reviewerName', 'reviewText', 'reviewDate', 'dateOfStay', 'tripType',
                             'reviewHelpfulVotes', 'cleanlinessRating', 'serviceRating', 'valueRating',
                             'includingImage', 'imageNum', 'roomsRating', 'sleepQualityRating', 'locationRating',
                             'reviewerURL', 'reviewerCityNum', 'contributorLevel', 'reviewerGender', 'reviewerAge',
                             'reviewerPhotoNum', 'reviewerContributionNum', 'reviewerHelpfulVotes', 'travelerType',
                             'reviewerExcellentRating',
                             'reviewerVeryGoodRating', 'reviewerAverageRating', 'reviewerPoorRating',
                             'reviewerTerribleRating', 'reviewerFollowingNum',
                             'reviewerFollowerNum', 'reviewerContributionNum2', 'reviewerLocation', 'registerMonth',
                             'reviewerTotalPoints',
                             'reviewerBadgeNum', 'reviewCrawledDate'))
            csvfile.close()
        csvfile = open(fn, 'r', encoding='utf-8')
        reader = csv.reader(csvfile)
        hotel_get = []
        review_get = []
        for line in reader:
            hotel_get.append(line[2])
            review_get.append(line[23])
        csvfile.close()
        count = Counter(hotel_get)
        hotels_file = hotelCity + '_hotels.txt'
        hotels = []
        with open(hotels_file, "r") as file:
            for line in file.readlines():
                line = line.strip('\n')
                hotels.append(line)
        hotel_urls = hotels
        print('这个城市的所有宾馆列表如下：')
        print(hotel_urls)
        cityHotelNum = len(hotel_urls)
        print('这个城市的一共有%s家宾馆。 '%cityHotelNum)
        print('\n')
        for hotel_url in hotel_urls:
            print('我在爬这家宾馆的数据：' + hotel_url)
            print('进度：%d/%d' % (hotel_urls.index(hotel_url), len(hotel_urls)))
            hotelURL = hotel_url
            code = re.findall('d\d+(?=-)', hotel_url)
            hotelCode = code[0]
            print('这家宾馆的id：',end='')
            print(hotelCode)
            name = re.findall('(?<=Reviews-).*(?=-)', hotel_url)
            hotelName = name[0]
            print('这家宾馆的名称：', end='')
            print(hotelName)
            review_page_urls, hotelReviewNum, hotelRankInCity, hotelOverallRating, hotelAddress, \
            hotelClass, hotelAwards, hotelStyle, hotelRoomTypes, hotelRoomNum, \
            hotelPriceRange, hotelLocation, hotelRatingExcellent, \
            hotelRatingVeryGood, hotelRatingAverage, hotelRatingPoor, \
            hotelRatingTerrible = find_hotel_page_data(hotel_url)
            print('这家宾馆的所有评论页面列表如下:')
            print(review_page_urls)
            print('this hotel has about %d reviews.Please wait,I will get it.' % (hotelReviewNum))
            print('这家宾馆的排名：',end='')
            print(hotelRankInCity)
            print('这家宾馆的总体评级：',end='')
            print(hotelOverallRating)
            print('这家宾馆的地址：',end='')
            print(hotelAddress)
            print('这家宾馆的星级：',end='')
            print(hotelClass)
            print('这家宾馆的荣誉：',end='')
            print(hotelAwards)
            print('这家宾馆的风格：',end='')
            print(hotelStyle)
            print('这家宾馆的房间类型：',end='')
            print(hotelRoomTypes)
            print('这家宾馆的房间数目：',end='')
            print(hotelRoomNum)
            print('这家宾馆的价格范围：',end='')
            print(hotelPriceRange)
            print('这家宾馆的详细地址：',end='')
            print(hotelLocation)
            print('这家宾馆的评论分布：',end='')
            print(hotelRatingExcellent, hotelRatingVeryGood, hotelRatingAverage, hotelRatingPoor, hotelRatingTerrible)
            if hotelCode in hotel_get and count[hotelCode] == hotelReviewNum:
                review_urls = []
            else:
                review_urls = find_review_urls(review_page_urls)
            print(review_urls)
            print("master,I get %d reviews."%(len(review_urls)))
            print('\n')
            if review_urls == []:
                if hotelCode not in hotel_get:
                    reviewURL = reviewTool = reviewRating = reviewTitle = reviewerName = reviewText = reviewDate = dateOfStay = tripType \
                        = reviewHelpfulVotes = cleanlinessRating = serviceRating = valueRating = \
                        includingImage = imageNum = roomsRating = sleepQualityRating = locationRating = \
                        reviewerURL = reviewerCityNum = contributorLevel = reviewerGender = reviewerAge = reviewerPhotoNum \
                        = reviewerContributionNum = reviewerHelpfulVotes = travelerType = reviewerExcellentRating \
                        = reviewerVeryGoodRating = reviewerAverageRating = reviewerPoorRating = reviewerTerribleRating = \
                        reviewerFollowingNum = reviewerFollowerNum = reviewerContributionNum2 = reviewerLocation = \
                        registerMonth = reviewerTotalPoints = reviewerBadgeNum = None
                    reviewCrawledDate = time.strftime('%Y/%m/%d', time.localtime(time.time()))
                    csvfile = open(fn, 'a+', encoding='utf-8', newline='')
                    writer = csv.writer(csvfile)
                    writer.writerow((cityCode, hotelURL, hotelCode, hotelCity, cityHotelNum, hotelRankInCity,
                                     hotelName, hotelReviewNum, hotelOverallRating, hotelAddress, hotelClass,
                                     hotelAwards, hotelStyle, hotelRoomTypes, hotelRoomNum, hotelPriceRange,
                                     hotelLocation, hotelReviewNum, hotelRatingExcellent, hotelRatingVeryGood,
                                     hotelRatingAverage, hotelRatingPoor, hotelRatingTerrible, reviewURL, reviewTool,
                                     reviewRating, reviewTitle,
                                     reviewerName, reviewText, reviewDate, dateOfStay, tripType,
                                     reviewHelpfulVotes, cleanlinessRating, serviceRating, valueRating,
                                     includingImage, imageNum, roomsRating, sleepQualityRating, locationRating,
                                     reviewerURL, reviewerCityNum, contributorLevel, reviewerGender,
                                     reviewerAge, reviewerPhotoNum, reviewerContributionNum, reviewerHelpfulVotes,
                                     travelerType, reviewerExcellentRating,
                                     reviewerVeryGoodRating, reviewerAverageRating, reviewerPoorRating,
                                     reviewerTerribleRating, reviewerFollowingNum,
                                     reviewerFollowerNum, reviewerContributionNum2, reviewerLocation,
                                     registerMonth, reviewerTotalPoints, reviewerBadgeNum, reviewCrawledDate))
                    csvfile.close()

            else:
                for reviewURL in review_urls:
                    if reviewURL not in review_get:
                        print('我在抓这个评论的：', end='')
                        print(reviewURL)
                        idObj = re.search('(?<=r)\d+', reviewURL)
                        id = idObj.group()
                        text = load_soup_review(id)
                        # print(text)
                        noquotes = text.find_all('span', class_='noQuotes')
                        title = re.search('(?<=>)[\s\S]*(?=<)', str(noquotes[0]))
                        reviewTitle = title.group()
                        print('评论题目是：', end='')
                        print(reviewTitle)
                        p = text.find_all('p', class_='partial_entry')
                        body = re.search('(?<=>).*(?=<)', str(p[0]))
                        reviewText = re.sub('<br>|<br/>', '', body.group())
                        print('评论内容是：', end='')
                        print(reviewText)
                        info_text = text.find_all('span', class_='expand_inline scrname')
                        contributor_name = re.search('(?<=>).*(?=</span>)', str(info_text[0]))
                        reviewerName = contributor_name.group()
                        print('评论者姓名：', end='')
                        print(reviewerName)
                        ratingDate = text.find_all('span', class_='ratingDate')
                        review_date = re.search('(?<=title=").*(?=">)', str(ratingDate[0]))
                        time_format = datetime.datetime.strptime(review_date.group(), '%B %d, %Y')
                        reviewDate = time_format.strftime('%Y/%m/%d')
                        print('评论日期：', end='')
                        print(reviewDate)
                        via_mobile = text.find_all('span', class_='viaMobile')
                        if via_mobile == []:
                            reviewTool = 'others'
                        else:
                            reviewTool = 'viaMobile'
                        print('评论方式：', end='')
                        print(reviewTool)
                        ratingObj = re.search('(?<=span class="ui_bubble_rating bubble_)\d(?=0)', str(text))
                        reviewRating = ratingObj.group()
                        print('评论等级：', end='')
                        print(reviewRating)
                        try:
                            stay = text.find('div', class_='prw_rup prw_reviews_stay_date_hsx')
                            stay_dateObj = re.search('(?<=Date of stay: ).*', stay.text)
                            time_format = datetime.datetime.strptime(stay_dateObj.group(), '%B %Y')
                            dateOfStay = time_format.strftime('%Y/%m/01')
                        except:
                            dateOfStay = None
                        print('逗留年月：', end='')
                        print(dateOfStay)
                        try:
                            travel_type = re.search(
                                '(?<=<span class="trip_type_label">Trip type: </span>).*?(?=</div>)',
                                str(text))
                            tripType = travel_type.group()
                        except:
                            tripType = None
                        print('出行类型：', end='')
                        print(tripType)
                        help_vote = text.find('span', class_='numHelp emphasizeWithColor')
                        reviewHelpfulVotes = help_vote.text
                        print('有用投票数目：', end='')
                        print(reviewHelpfulVotes)
                        recommend_answer = text.find_all('li', class_='recommend-answer')
                        cleanlinessRating = serviceRating = valueRating = roomsRating = sleepQualityRating = locationRating = None
                        for answer in recommend_answer:
                            item_div = answer.find('div', class_='recommend-description')
                            item = item_div.text
                            if item == 'Location':
                                locationObj = re.search('\d', str(answer))
                                locationRating = int(locationObj.group())
                            elif item == 'Value':
                                valueObj = re.search('\d', str(answer))
                                valueRating = int(valueObj.group())
                            elif item == 'Sleep Quality':
                                sleepqualityObj = re.search('\d', str(answer))
                                sleepQualityRating = int(sleepqualityObj.group())
                            elif item == 'Cleanliness':
                                cleanlinessObj = re.search('\d', str(answer))
                                cleanlinessRating = int(cleanlinessObj.group())
                            elif item == 'Service':
                                serviceObj = re.search('\d', str(answer))
                                serviceRating = int(serviceObj.group())
                            elif item == 'Rooms':
                                roomsObj = re.search('\d', str(answer))
                                roomsRating = int(roomsObj.group())
                        print('各方面评级：', end='')
                        print(cleanlinessRating, serviceRating, valueRating, roomsRating, sleepQualityRating,
                              locationRating)
                        photocontainer = text.find_all('div', class_='photoContainer')
                        imageNum = len(photocontainer)
                        if imageNum > 0:
                            includingImage = 1
                        else:
                            includingImage = 0
                        print('是否有图片：', end='')
                        print(includingImage)
                        print('图片数量：', end='')
                        print(imageNum)
                        uid_src = text.find_all('div', class_='member_info')
                        uidObj = re.search('(?<=UID_).*?(?=-SRC_)', str(uid_src[0]))
                        try:
                            uid = uidObj.group()
                            # print(uid)
                            srcObj = re.search('(?<=SRC_)\d+', str(uid_src[0]))
                            src = srcObj.group()
                            # print(src)
                            contributor_text = load_soup_contributor(uid, src)
                            contributor_urlObj = re.search('/Profile.*(?=")', str(contributor_text))
                            reviewerURL = 'https://www.tripadvisor.com' + contributor_urlObj.group()
                            print("评论者链接是：", end='')
                            print(reviewerURL)
                            try:
                                badgeinfo = contributor_text.find_all('div', class_='badgeinfo')
                                contributor_LevelObj = re.search('\d', str(badgeinfo[0]))
                                contributorLevel = contributor_LevelObj.group()
                            except:
                                contributorLevel = None
                            print("评论者等级：", end='')
                            print(contributorLevel)

                            memberdescription = contributor_text.find('ul',
                                                                      class_='memberdescriptionReviewEnhancements')
                            # print(memberdescription.text)
                            genderObj = re.search('man(?= from)|Man(?= from)|woman(?= from)|Woman(?= from)',
                                                  memberdescription.text)
                            try:
                                reviewerGender = genderObj.group()
                                reviewerGender = reviewerGender.lower()
                            except:
                                reviewerGender = None
                            print("评论者性别：", end='')
                            print(reviewerGender)
                            ageObj = re.search('\d+-\d+|\d+\+', memberdescription.text)
                            try:
                                reviewerAge = ageObj.group()
                            except:
                                reviewerAge = None
                            print("评论者年龄：", end='')
                            print(reviewerAge)
                            try:
                                memberTagReview = contributor_text.find('a', class_='memberTagReviewEnhancements')
                                travelerType = memberTagReview.text
                            except:
                                travelerType = None
                            print("评论者类型：", end='')
                            print(travelerType)
                            badgeTextReviewEnhancements = contributor_text.find_all('span',
                                                                                    class_='badgeTextReviewEnhancements')
                            reviewerContributionNum = reviewerCityNum = reviewerPhotoNum = reviewerHelpfulVotes = None
                            for badgetext in badgeTextReviewEnhancements:
                                bandgetypeObj = re.search('(?<=\d\s).*(?=</span>)', str(badgetext))
                                bandgetype = bandgetypeObj.group()
                                if bandgetype == 'Contributions' or bandgetype == 'Contribution':
                                    contributionsObj = re.search('\d+', str(badgetext))
                                    reviewerContributionNum = contributionsObj.group()
                                elif bandgetype == 'Cities visited' or bandgetype == 'City visited':
                                    contributor_cities_visitedObj = re.search('\d+', str(badgetext))
                                    reviewerCityNum = contributor_cities_visitedObj.group()
                                elif bandgetype == 'Helpful votes' or bandgetype == 'Helpful vote':
                                    contributor_helpful_votesObj = re.search('\d+', str(badgetext))
                                    reviewerHelpfulVotes = contributor_helpful_votesObj.group()
                                elif bandgetype == 'Photos' or bandgetype == 'Photo':
                                    contributor_photosObj = re.search('\d+', str(badgetext))
                                    reviewerPhotoNum = contributor_photosObj.group()
                            print('评论者评论总数，访问城市数目，发表照片数目，获得有用投票总数：', end='')
                            print(reviewerContributionNum, reviewerCityNum, reviewerHelpfulVotes, reviewerPhotoNum)
                            chartRowReviewEnhancements = contributor_text.find_all('div',
                                                                                   class_='chartRowReviewEnhancements')
                            reviewerExcellentRating = reviewerVeryGoodRating = reviewerAverageRating = reviewerPoorRating = reviewerTerribleRating = None
                            for chartRow in chartRowReviewEnhancements:
                                chartRowObj = re.search('(?<=>).*(?=</span>)', str(chartRow))
                                chartRowtype = chartRowObj.group()
                                if chartRowtype == 'Excellent':
                                    contributor_review_excellentObj = re.search('\d+(?=</span>)', str(chartRow))
                                    reviewerExcellentRating = contributor_review_excellentObj.group()
                                elif chartRowtype == 'Very good':
                                    contributor_review_goodObj = re.search('\d+(?=</span>)', str(chartRow))
                                    reviewerVeryGoodRating = contributor_review_goodObj.group()
                                elif chartRowtype == 'Average':
                                    contributor_review_averageObj = re.search('\d+(?=</span>)', str(chartRow))
                                    reviewerAverageRating = contributor_review_averageObj.group()
                                elif chartRowtype == 'Poor':
                                    contributor_review_poorObj = re.search('\d+(?=</span>)', str(chartRow))
                                    reviewerPoorRating = contributor_review_poorObj.group()
                                elif chartRowtype == 'Terrible':
                                    contributor_review_terribleObj = re.search('\d+(?=</span>)', str(chartRow))
                                    reviewerTerribleRating = contributor_review_terribleObj.group()
                            print("各星评论数目：", end='')
                            print(reviewerExcellentRating, reviewerVeryGoodRating, reviewerAverageRating,
                                  reviewerPoorRating,
                                  reviewerTerribleRating)

                            profile = load_soup_online(reviewerURL)
                            reviewerships = profile.find_all('span',
                                                             class_='social-common-MemberStats__stat_item_count--15EgC')
                            reviewerContributionNum2 = re.sub(',', '', reviewerships[0].text)
                            reviewerFollowerNum = re.sub(',', '', reviewerships[1].text)
                            reviewerFollowingNum = re.sub(',', '', reviewerships[2].text)
                            print("评论者贡献数2，评论者粉丝数，评论者关注用户数：", end='')
                            print(reviewerContributionNum2, reviewerFollowerNum, reviewerFollowingNum)
                            try:
                                location = profile.find('span',
                                                        class_='social-common-MemberInfo__member_info--3mJe_ social-common-MemberHometown__hometown---q2h5 default')
                                reviewerLocation = location.text
                            except:
                                reviewerLocation = None
                            print("评论者所在地:", end='')
                            print(reviewerLocation)
                            joindate = profile.find('span', class_='social-common-MemberCreated__memberCreated--D9VqB')
                            time_format = datetime.datetime.strptime(joindate.text, 'Joined in %b %Y')
                            registerMonth = time_format.strftime('%Y/%m/01')
                            print("评论者注册年月:", end='')
                            print(registerMonth)
                            bandgeURL = re.sub('Profile', 'members-badgecollection', reviewerURL)
                            badge = load_soup(bandgeURL)
                            if badge == '':
                                reviewerTotalPoints = reviewerBadgeNum = None
                            else:
                                points = badge.find('div', class_='points')
                                reviewerTotalPoints = re.sub(',', '', points.text)
                                print('评论者总分:', end='')
                                print(reviewerTotalPoints)
                                badgenum = badge.find('div', class_='modules-membercenter-badge-collection-header ')
                                reviewerBadgeNumObj = re.search('(?<=<span>)\d+?(?=</span>)', str(badgenum))
                                reviewerBadgeNum = re.sub(',', '', reviewerBadgeNumObj.group())
                                print("评论者勋章总数:", end='')
                                print(reviewerBadgeNum)
                        except:
                            reviewerURL = reviewerCityNum = contributorLevel = reviewerGender = reviewerAge = reviewerPhotoNum \
                                = reviewerContributionNum = reviewerHelpfulVotes = travelerType = reviewerExcellentRating \
                                = reviewerVeryGoodRating = reviewerAverageRating = reviewerPoorRating = reviewerTerribleRating = \
                                reviewerFollowingNum = reviewerFollowerNum = reviewerContributionNum2 = reviewerLocation = \
                                registerMonth = reviewerTotalPoints = reviewerBadgeNum = None
                        reviewCrawledDate = time.strftime('%Y/%m/%d', time.localtime(time.time()))
                        print('爬取评论日期:', end='')
                        print(reviewCrawledDate)
                        csvfile = open(fn, 'a+', encoding='utf-8', newline='')
                        writer = csv.writer(csvfile)
                        writer.writerow((cityCode, hotelURL, hotelCode, hotelCity, cityHotelNum, hotelRankInCity,
                                         hotelName, hotelReviewNum, hotelOverallRating, hotelAddress, hotelClass,
                                         hotelAwards, hotelStyle, hotelRoomTypes, hotelRoomNum, hotelPriceRange,
                                         hotelLocation, hotelReviewNum, hotelRatingExcellent, hotelRatingVeryGood,
                                         hotelRatingAverage, hotelRatingPoor, hotelRatingTerrible, reviewURL,
                                         reviewTool,
                                         reviewRating, reviewTitle,
                                         reviewerName, reviewText, reviewDate, dateOfStay, tripType,
                                         reviewHelpfulVotes, cleanlinessRating, serviceRating, valueRating,
                                         includingImage, imageNum, roomsRating, sleepQualityRating, locationRating,
                                         reviewerURL, reviewerCityNum, contributorLevel, reviewerGender,
                                         reviewerAge, reviewerPhotoNum, reviewerContributionNum, reviewerHelpfulVotes,
                                         travelerType, reviewerExcellentRating,
                                         reviewerVeryGoodRating, reviewerAverageRating, reviewerPoorRating,
                                         reviewerTerribleRating, reviewerFollowingNum,
                                         reviewerFollowerNum, reviewerContributionNum2, reviewerLocation,
                                         registerMonth, reviewerTotalPoints, reviewerBadgeNum, reviewCrawledDate))
                        csvfile.close()
                        print('\n')

    endtime = datetime.datetime.now()
    print('程序执行时间(s)：',end = '')
    print((endtime - starttime).seconds)



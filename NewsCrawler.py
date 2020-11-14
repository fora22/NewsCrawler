# -*- coding: utf-8 -*-
"""NewsCrawler.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1LuNJG3M4rZunqkPH4L_7u6Ig8Y0PzQE8
"""

import os
import urllib.request
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import quote

import pandas as pd



class NewsCrawler():
    def __init__(self, searchWord, countNews):
        self.countNews = countNews
        self.searchWord = quote(searchWord)
        self.searchKeyword = searchWord

    def GetBs4Object(self, URL):    # bs4의 Beautifulsoup를 통해 bs4 object를 구하는 함수
        try:
            URL_Headers = urllib.request.Request(URL, headers={'User-Agent':'Mozilla/5.0'})
            HTML = urlopen(URL_Headers)
            decodeHTML = HTML.read()# .decode('utf-8')
            bs4Object = BeautifulSoup(decodeHTML, "html.parser")

            return bs4Object
        except:
            return " "

    def GetNewsLink(self, searchWindowObject):
        result = []
        for newsLink in searchWindowObject.find_all("dd","txt_inline"):
            for naverNews in newsLink.find_all("a","_sp_each_url"):
                if "href" in naverNews.attrs:
                    result.append(naverNews.attrs["href"])
        # Naver에서 검색어로 검색한 기사 창에 네이버 뉴스로 볼 수 있는 링크만 가져옴
        return result

    def GetNewsData(self, link):
        linkObject = self.GetBs4Object(link)
        newsDate = self.GetNewsDate(linkObject)
        newsBody = self.GetNewsBody(linkObject)
        
        return newsDate, newsBody
    
    def GetNewsDate(self, newsObject_for_Date):
        try:
            # 2020.09.21. 오후 3:15 형식으로 뜨기 때문에 앞에 11글자만 가져옴
            newsData = newsObject_for_Date.find("span", "t11").get_text()[:12]
            if newsData == None:
                return " "
            else:
                return newsData
        except:
            return " "

    def GetNewsBody(self, newsObject_for_Body):
        try:
            for deleteTag in newsObject_for_Body.find_all(["script", "span", "a"]):
                deleteTag.extract()             # extract 함수는 bs4 객체에서 해당 태그를 제거한다.

            newsContents = newsObject_for_Body.find("div", "_article_body_contents")     # 그 다음 기사 내용을 찾는다.
            newsBody = (newsContents.get_text("\n", strip=True))
            if newsBody == None:
                return " "
            else:
                return newsBody
        except:
            return " "

    def CrawlerStart(self):
        dfList = []     # DataFrame을 보관하는 List

        # 뉴스페이지가 검색창에서 약 10개씩 나오므로 8을 빼서 URL에 들어가는 숫자를 맞춰줌
        # for newsPageNumber in range(1, self.countNews - 8, 10):
        while (len(dfList) < self.countNews):        # countNews만큼 기사가 모일때까지 반복문 돌림
            searchURL = ("https://search.naver.com/search.naver?&where=news&query="
            + self.searchWord + "&sm=tab_pge&sort=0&photo=0&field=0&reporter_article=&pd=0&ds=&de=&docid=&nso=so:r,p:all,a:all&mynews=0&cluster_rank=65&start=" 
            + str(newsPageNumber) + "&refresh_start=0")
            
            searchHTMLObejct = self.GetBs4Object(searchURL)         # 검색창의 HTML bs4 Object를 가져옴
            searchNewsLinkList = self.GetNewsLink(searchHTMLObejct)     # 네이버 뉴스 형식이 지원되는 News Link만 가져옴
            
            urlList = []    # url을 저장하는 리스트
            dateList = []   # 날짜를 저장하는 리스트
            newsList = []   # 기사 내용을 저장하는 리스트

            for searchNewsLink in searchNewsLinkList:
                date, news = self.GetNewsData(searchNewsLink)
                urlList.append(searchNewsLink)
                dateList.append(date)
                newsList.append(news)

            newsData = {"URL": urlList, "Date" : dateList, "Article" : newsList}
            dfList.append(pd.DataFrame(newsData))

        for i in range(len(dfList)):
            if i == 0:
                resultDF = dfList[0]
            else:
                resultDF = pd.concat([resultDF, dfList[i]])

        print(resultDF)
        resultDF.to_excel('CrawlingData/' + self.searchKeyword + " 약 " + str(self.countNews) + "개" + '_News.xlsx')

if __name__ == "__main__":
    if not(os.path.exists('CrawlingData')):
        os.makedirs("CrawlingData")

    searchCommand = input("검색어를 입력하세요 : ")
    newsNumber = int(input("10개단위로 숫자를 입력해주세요(1 ~ N). : "))
    n = NewsCrawler(searchCommand, newsNumber)
    n.CrawlerStart()
    

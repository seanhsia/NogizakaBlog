# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 18:16:20 2020

@author: Sean Hsia
"""
import os
from sys import exit
import re

import json
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from pdb import set_trace as st

        
        
        
class APICrawler():
    def __init__(self, member_name='all'):
        self.member_name = member_name
        self.base_url ="https://www.nogizaka46.com/"
        self.blog_api_base="https://www.nogizaka46.com/s/n46/api/list/blog"
        self.feature_list = []
        self.name_kanji_to_katakana = {
            "秋元 真夏": "manatsu.akimoto",
            "伊藤 理々杏": "riria.itou",
            "岩本 蓮加": "renka.iwamoto",
            "梅澤 美波": "minami.umezawa",
            "北野 日奈子": "hinako.kitano",
            "久保 史緒里": "shiori.kubo",
            "齋藤 飛鳥": "asuka.saito",
            "阪口 珠美": "tamami.sakaguchi",
            "佐藤 楓": "kaede.satou",
            "鈴木 絢音": "ayane.suzuki",
            "中村 麗乃": "reno.nakamura",
            "樋口 日奈": "hina.higuchi",
            "向井 葉月": "hazuki.mukai",
            "山崎 怜奈": "rena.yamazaki",
            "山下 美月": "mizuki.yamashita",
            "吉田 綾乃クリスティー": "ayanochristie.yoshida",
            "与田 祐希": "yuuki.yoda",
            "和田 まあや": "maaya.wada",
            "遠藤 さくら": "sakura.endou",
            "賀喜 遥香": "haruka.kaki",
            "掛橋 沙耶香": "sayaka.kakehashi",
            "金川 紗耶": "saya.kanagawa",
            "北川 悠理": "yuri.kitagawa",
            "柴田 柚菜": "yuna.shibata",
            "清宮 レイ": "rei.seimiya",
            "田村 真佑": "mayu.tamura",
            "筒井 あやめ": "ayame.tsutsui",
            "早川 聖来": "seira.hayakawa",
            "矢久保 美緒": "mio.yakubo",
            "黒見明香": "haruka.kuromi",
            "佐藤璃果": "rika.satou",
            "林瑠奈" : "runa.hayashi",
            "松尾美佑": "miyu.matsuo",
            "弓木奈於": "nao.yumiki",
            "新4期生リレー": "newfourth",
            "運営スタッフ": "staff",
            "研究生": "kenkyusei",
            "３期生": "third",
            "４期生": "fourth"
        }
    def createFakeUserAgentHeader(self):
        '''
        Returns
        -------
        header : dict
            header like browser

        '''
        ua = UserAgent(use_cache_server=True)        
        header = {'User-Agent':str(ua.random)}
        return header


    def apiTextToJson(self, text):
        return json.loads(text[4:-2])

    def createConnection(self, url):
        '''
        This function creates connection with nogizaka official blog websites
        through fake user agent(browser header)

        Returns
        -------
        soup : Beautiful soup object
            html context of blog page

        '''
        #Create fake user agent
        header = self.createFakeUserAgentHeader()
        res = requests.get(url, headers=header)
        
        if res.status_code == 200:
            #print("url: ", url)
            #Connection Success
            res.encoding = 'utf-8'
            return res.text          
        else:
            #Connection Fail
            print("url: ", url)
            print("status: ", res.status_code)
            exit(1)

    def getApiData(self, url):
        text = self.createConnection(url)
        res_json = self.apiTextToJson(text)
        return res_json

    def getTotalBlogCount(self):
        blog_data = self.getApiData(self.blog_api_base + '?rw=0')
        return blog_data['count']
    
    def getCommentsNum(self, blog_id):
        comment_data=self.getApiData(f"https://www.nogizaka46.com/s/n46/api/list/comment?kiji={blog_id}&rw=0&st=0")
        return comment_data['count']

    def getBlogData(self, mode, all=False, start_index=0, data_per_request=100):
        total_blog_count = int(self.getTotalBlogCount())
        if mode=="update":
            for i in range(start_index, total_blog_count, data_per_request):
                # rw: 一次拉多少資料
                # st: 從第幾個index開始拉(跟據日期降序)
                url = self.blog_api_base + f'?rw={data_per_request}&st={i}'
                data = self.getApiData(url)
                data = data['data']

                for blog in data:
                    blog_id, title, author, date, context, img_urls = self.parse(blog)
                    n_comments = self.getCommentsNum(blog_id)
                    info = (author, title, date, n_comments)
                    print(f"Title: {title}\nAuthor: {author}\nDate: {date}\nNumber of Comments: {n_comments}")
                    existence = self.saveData(info, context, img_urls, update=True)
                    print(existence)
                    if existence and not all:
                        return
            return
        

    def parse(self, blog):
        blog_id = blog['code']
        title = blog['title']
        author = self.name_kanji_to_katakana[blog['name']]
        date = blog['date'][0:10]

        context_html = BeautifulSoup(blog['text'], 'html.parser')
        context = context_html.find_all(text=True)
        # remove space from the start or end of each senteces
        context = [sentence.strip('　') for sentence in context]            
        # add line change for reading
        context = "\n\n".join(context)
            
        img_urls = [ self.base_url+ img['src'] for img in context_html.findAll('img') if img.has_attr('src')]
        return blog_id, title, author, date, context, img_urls

    def saveData(self, info, text, img_urls, update):
        author, title, date, comments_num = info
        char_num = len(text.replace("\n", ""))
        img_num = len(img_urls)
        
        feature = {"Author": author,
                   "Title": title,
                   "Date": date,
                   "Number of Comments": comments_num,
                   "Number of Characters in Title": len(title),
                   "Number of Characters in Context": char_num,
                   "Number of Images": img_num,
                   "Urls of Images": json.dumps(img_urls)}
        
        
        
        path = os.path.join(os.getcwd(), 'blogs\\', author+'\\')
        
        #To make sure the file name is valid for windows environment
        date = date.replace('/', '.')
        rx = re.compile(r'([*|\\:"<>?/\n\r\t])')
        title = rx.sub("", title)[:100]
        
        
        if not self.fileExists(path, title, date):
            #write text file and download all images
            path = os.path.join(path, date + '_' + title + '\\', date + '_' + title + '.txt')
            print("writing file... ", path)
            self.writeFile(text, path)
            for i, url in enumerate(img_urls):
                self.downloadImage(url, 
                    os.path.join(os.path.dirname(path), str(i) + '.jpeg'))
            feature["Context Path"] = path
            self.feature_list.append(feature)
        
        elif update:
            existence = self.fileExists(path, title, date)
            path = os.path.join(path, date + '_' + title + '\\', date + '_' + title + '.txt')
            feature["Context Path"] = path
            self.feature_list.append(feature)
            return existence
        
        else:
            path = os.path.join(path, date + '_' + title + '\\', date + '_' + title + '.txt')
            feature["Context Path"] = path
            self.feature_list.append(feature)
    
    def fileExists(self, path, title, date):
        '''
        This function check if this blog was saved before.

        Parameters
        ----------
        path : string
            path containing author's name
        title : string
            the title of the blog
        date : date
            the upload date of the blog

        Returns
        -------
        bool
            whether this blog was saved or not

        '''
        
        if os.path.isdir(path):
            #directory exists
            path = os.path.join(path, date + '_' + title + '\\')
            
            if os.path.isdir(path):
                #directory exists
                path = os.path.join(path, date + '_' + title + '.txt')
                
                if os.path.isfile(path):
                    #file exists
                    return True
                
                else:
                    return False
                
            else:
                #No directory exists, so create one
                os.mkdir(path)
                return False
                
        else:
            #No directory exists, so create one
            os.mkdir(path)
            path = os.path.join(path, date + '_' + title + '\\')
            os.mkdir(path)
            return False
    
    def downloadImage(self, url, path):
        '''
        This function downloads a image from a certain url

        Parameters
        ----------
        url : string
            the url of the image
        path : string
            the path where we store the image

        Returns
        -------
        None.

        '''
        if url[:4] != "http":
            return
        
        header = self.createFakeUserAgentHeader()
        
        try:
            res = requests.get(url, headers=header)
        except requests.exceptions.HTTPError as errh:
            print ("Http Error:",errh)
            return
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:",errc)
            return
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:",errt)
            return
        except requests.exceptions.RequestException as err:
            print ("OOps: Something Else",err)
            return
                
        if res.status_code == 200:
            with open(path, 'wb') as file:
                file.write(res.content)
        else:
            print("status: ", res.status_code)
            print("url: ", url)
            print("Failed to download this image")
            
    def writeFile(self, text, path):
        '''
        This function writes blog context to a text file
        
        Parameters
        ----------
        text : string
            context of the blog
        path : string
            the path where we store the text file

        Returns
        -------
        None.

        '''
        with open(path, 'w', encoding='utf-8') as file:
            file.write(text)

if __name__ == '__main__':
    crawler= APICrawler()
    crawler.getBlogData(mode="update")

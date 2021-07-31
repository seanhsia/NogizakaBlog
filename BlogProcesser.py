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




class BlogProcesser():
    def __init__(self, member_name='all'):
        self.member_name = member_name
        self.base_url = "http://blog.nogizaka46.com/"
        self.feature_list = []
        
    def crawling(self):
        soup = self.createConnection(self.base_url)
        self.processData(soup)
            
    def processData(self, soup):
        member_names = self.getMemberNames(soup)
        urls = self.getMemberBlogUrls(soup)
        
        if self.member_name == 'all':
            for url in urls:
                monthly_blog_urls = self.getMonthlyBlogUrls(url)
                for blog_url in monthly_blog_urls:
                    blog_soup = self.createConnection(blog_url)                    
                    while True:
                        paginate = blog_soup.find('div', {'class': 'paginate'})
                        blogs_num = len(blog_soup.findAll('h1', {'class': 'clearfix'}))
                        entry_num = len(blog_soup.findAll('div', {'class': 'entrybody'}))
                        
                        while blogs_num != entry_num:
                            #Reconnect
                            print("body: ", entry_num)
                            print("titles: ", blogs_num)
                            print("Reconnecting ...")
                            blog_soup = self.createConnection(blog_url)
                            paginate = blog_soup.find('div', {'class': 'paginate'})
                            blogs_num = len(blog_soup.findAll('h1', {'class': 'clearfix'}))
                            entry_num = len(blog_soup.findAll('div', {'class': 'entrybody'}))                            
                        
                        self.getBlogsContext(blog_soup, author=url)
                        
                        #There is a next page
                        if paginate is not None and '＞' == paginate.findAll('a')[-1].text:
                            parameters=blog_soup.find('div', {'class': 'paginate'}).findAll('a')[-1]['href']
                            blog_url = self.base_url + url + '/' + parameters
                            blog_soup = self.createConnection(blog_url)
                        
                        #Next page doesn't exist
                        else:
                            break
                        
        elif self.member_name in set(member_names):
            pass
    
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
            print("url: ", url)
            #Connection Success
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            return soup            
        else:
            #Connection Fail
            print("url: ", url)
            print("status: ", res.status_code)
            exit(1)
            
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
            
            
    def getBlogsContext(self, soup, author, update=False):

        infos = self.getBlogsInfo(soup, author)
                                 
        for i, blog in enumerate(soup.findAll('div', {'class': 'entrybody'})):
            # a list contains one sentence in each entry
            context = blog.find_all(text=True)
            # remove space from the start or end of each senteces
            context = [sentence.strip('　') for sentence in context]            
            # add line change for reading
            context = "\n\n".join(context)
            
            img_urls = [ img['src'] for img in blog.findAll('img') if img.has_attr('src')]
            
            existence = self.saveData(infos[i], context, img_urls, update)
            
            if existence is not None and existence is True and update is True:
                return existence
            
        return False
            
    def getBlogsInfo(self, soup, author):
        blogs_num = len(soup.findAll('h1', {'class': 'clearfix'}))
        
        #Get blog titles
        titles = [ tag.find('a').text for tag in soup.findAll('h1', {'class': 'clearfix'})]
        
        #Get the date when the blog was posted
        dates = [ tag.find('span', {'class': 'yearmonth'}).text +
                 '/' +
                  tag.find('span', {'class': 'dd1'}).text
                  for tag in soup.findAll('h1', {'class': 'clearfix'})]
        
        #Get the amount of comments
        comments_atags = soup.find_all('a', {'href': re.compile(r'#comments')})
        nums_rx = re.compile(r'[0-9]+')
        comments_nums = [ nums_rx.search(comments_atag.text).group(0) for comments_atag in comments_atags]
        
        
        if type(author) is str:
            authors = [author] * blogs_num
        else:
            assert blogs_num == len(author), 'Missing author X_X'
            authors = author
        
        infos = list(zip(authors, titles, dates, comments_nums))
        
        assert blogs_num == len(infos),'The amount of infos must equal to the amount of blogs'
        
        return infos
    
    
        
    def getMonthlyBlogUrls(self, url):
        '''
        

        Parameters
        ----------
        url : TYPE
            members blog url ex. http://blog.nogizaka46.com/erika.ikuta

        Returns
        -------
        monthly_blog_urls : list
            containing monthly blog urls based on members

        '''
        archive_soup = self.createConnection(self.base_url + url + '/?d=archives')
        while archive_soup.find('div', {'class': 'archive-content'}) is None:
            archive_soup = self.createConnection(self.base_url + url + '/?d=archives')
        a_list = archive_soup.find('div', {'class': 'archive-content'}).findAll('a')
        monthly_blog_urls = [ a['href'] for a in a_list]
        
        
        return monthly_blog_urls
    
    def getMemberNames(self,soup):
        '''
        This function collects member's name on nogizaka official blog website
        
        Parameters
        ----------
        soup : Beautiful soup object
            html context of "http://blog.nogizaka46.com/"

        Returns
        -------
        list 
            contains member names in kanji, hiragana or katakana
        '''
        return [ tag.text for tag in soup.findAll('span', {'class': 'kanji'})]
    
    def getMemberBlogUrls(self, soup):
        '''
        

        Parameters
        ----------
        soup : Beautiful soup object
            html context of "http://blog.nogizaka46.com/"

        Returns
        -------
        urls : list
            contains the name of directory storing members' blog

        '''
        urls = [ tag.find('a')['href'][2:] 
                for tag in soup.findAll('div', {'class': 'unit'})]
        
        urls += [ a['href'][2:] 
                 for tag in soup.findAll('div', {'class': 'unit2'})
                 for a in tag.findAll('a')]           
        return urls
        
        
    def updateSavedBlogData(self):
        blog_url = self.base_url
        blog_soup = self.createConnection(blog_url)
        
        while True:
            paginate = blog_soup.find('div', {'class': 'paginate'})
            blogs_num = len(blog_soup.findAll('h1', {'class': 'clearfix'}))
            entry_num = len(blog_soup.findAll('div', {'class': 'entrybody'}))
            title_atags = blog_soup.findAll('a', {'rel': 'bookmark'})
            
            if title_atags is not None:
                authors = [ atag['href'].split('/')[3] for atag in title_atags]
            while blogs_num != entry_num or blogs_num != len(authors):
                #Reconnect
                print("body: ", entry_num)
                print("titles: ", blogs_num)
                print("Reconnecting ...")
                blog_soup = self.createConnection(blog_url)
                paginate = blog_soup.find('div', {'class': 'paginate'})
                blogs_num = len(blog_soup.findAll('h1', {'class': 'clearfix'}))
                entry_num = len(blog_soup.findAll('div', {'class': 'entrybody'}))                            
                title_atags = blog_soup.findAll('a', {'rel': 'bookmark'})
                if title_atags is not None:
                    authors = [ atag['href'].split('/')[3] for atag in title_atags]
            
            
            existence = self.getBlogsContext(blog_soup, author=authors, update=True)
            
            #File already exists            
            if existence:
                print("Update to the newest blog")
                break
            
            #There is a next page
            if paginate is not None and '＞' == paginate.findAll('a')[-1].text:
                parameters=blog_soup.find('div', {'class': 'paginate'}).findAll('a')[-1]['href']
                blog_url = self.base_url + '/' + parameters
                blog_soup = self.createConnection(blog_url)
                        
            #Next page doesn't exist
            else:
                break
        
        
        
        
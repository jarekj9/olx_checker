#!/usr/bin/env python3
from bs4 import BeautifulSoup
import time
import itertools
import requests
import re
import statistics


#progress indicator
class PROGRESS:
        def __init__(self):
                self.char=itertools.cycle('/-\|')
        def run(self):
                print(next(self.char), end = '\r')


class OLXJJ:
    def __init__(self,url):
        self.url=url
        #prepare data to parse (to discover links/pages)
        self.r  = requests.get(self.url)
        self.data = self.r.text
        self.soup = BeautifulSoup(self.data,features="html.parser")

        #get number of pages
        try:
            self.nr_of_pages = int(str(self.soup.find("a", {"data-cy": "page-link-last"})).split("page=")[1].split('"')[0])
        except:
            print("Problem to determine number of pages or there is only 1 page (nr_of_pages)")
            self.nr_of_pages=1
        self.progress=PROGRESS()
        self.percent_progress = 0
        
    #returns direct links to offers from single page
    def _get_links_from_page(self,soup):
        self.soup=soup
        self.righttab = self.soup.find("table", {"class": "fixed offers breakword redesigned"}) 
        self.offers=[]
        for link in self.righttab('a'):
            if "promoted" in str(link): continue    
            if "oferta" in str(link) and link.get('href') not in self.offers: self.offers.append(link.get('href'))
        return self.offers
        
    #returns offer links for all pages (combined)
    def _get_all_links(self):
        self.output=[]
        for self.page_nr in range(1,self.nr_of_pages+1):
            if self.url[-1:] == "/": self.r  = requests.get(self.url+"?page="+str(self.page_nr))  #because there are different versions of links
            else:                    self.r  = requests.get(self.url+"&page="+str(self.page_nr))
            self.data = self.r.text
            self.soup = BeautifulSoup(self.data,features="html.parser")
            for self.link in self._get_links_from_page(self.soup): self.output.append(self.link)
            self.progress.run()
        return self.output
        
    #returns dict with links, that include specific words in the page text, 
    #format: {link:[word1 with context, word2 with context....]}
    #if and_or equals "and", all words must be present in the link,
    #if it equals "or", any of words must be in the link
    #you can put many words as arguments or pass list with words
    def get_links_with_word(self,and_or,*words):    
        self.links=self._get_all_links()
        self.words=words
        if type(self.words[0]) == list: self.words = self.words[0]    #if list was passed as argument for words
        print (self.words)
        self.output={}
        
        for self.number,self.link in enumerate(self.links):
            print("Working for link "+str(self.number+1)+" of "+str(len(self.links)))
            self.r  = requests.get(self.link)
            self.data = self.r.text
            self.soup = BeautifulSoup(self.data,features="html.parser")
            
            #get description text
            self.description=""
            try: 
                self.description=self.soup.find("section", {"class": "section-description"}).find("div")   #for otodom
            except: 
                pass
            if not self.description: self.description=self.soup.find("div", {"class": "clr lheight20 large"})   #for olx
            if self.description == None: 
                print ("Did  not find any description on the offer page:")
                print(self.link)
                continue
            
            self.output_partial=[]
            hitcount=0
            for self.word in self.words:                    
                if re.findall(self.word,self.description.text):
                    hitcount+=1
                    self.output_partial.append(re.findall(".{25}"+self.word+".{25}",self.description.text))      #save link and word with chars around it
                    
            if and_or=="or" and hitcount : self.output.update({self.link:self.output_partial})
            if and_or=="and" and hitcount==len(self.words): self.output.update({self.link:self.output_partial})
            
        print("Done.")
        return self.output
        
    #returns list of prices for one page (bs4 object is passed as argument)    
    def _get_prices_from_page(self,soup, ignore_list):
        self.prices=[]
        self.soup=soup
        righttds = self.soup.find_all("td", {"class": "wwnormal tright td-price"})

        for righttd in righttds:
            if "promoted-list" in str(righttd.find_parent('table')):
                continue                                           #skip promoted offers (they double)
            if "<strong>" not in str(righttd) :
                continue                                            #because there are empty entries 

            offer_title = str(righttd.find_parent('table').find("strong").get_text())
            if self._title_matches_ignore_list(offer_title, ignore_list):
                continue

            for self.price in righttd:
                try:
                    self.price_int=self.price.find('strong').get_text()
                    if ',' in self.price_int: self.price_int=self.price_int.split(',')[0]     #sometimes price has comma
                    self.price_int=re.sub('\D','',self.price_int)                  #remove everything except digits
                    self.prices.append(int(self.price_int))
                except: pass    
        return self.prices

    def _title_matches_ignore_list(self, offer_title, ignore_list):
        for word in ignore_list:
            if word.casefold() in offer_title.casefold():
                return True
        return False

    #uses _get_prices_from_page for every page
    def get_all_prices(self, ignore_list):
        self.all_prices=[]
        self.sum=0
        self.count=0
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        }
        for self.page_nr in range(1,self.nr_of_pages+1):
            self.percent_progress = round((self.page_nr / self.nr_of_pages) * 100)
            print(f'Progress {self.percent_progress}')
            if self.url[-1:] == "/": self.r  = requests.get(self.url+"?page="+str(self.page_nr), headers=headers)  #because there are different versions of links, I want to move this to init
            else:                    self.r  = requests.get(self.url+"&page="+str(self.page_nr), headers=headers)

            self.data = self.r.text
            self.soup = BeautifulSoup(self.data,features="html.parser")
            self.page_prices=self._get_prices_from_page(self.soup, ignore_list)
            for self_price in self.page_prices: 
                self.all_prices.append(self_price)
                self.sum+=self_price
                self.count+=1

            self.progress.run()

        return {'prices': self.all_prices,
                'count': self.count,
                'average': self.sum//self.count,
                'median': int(statistics.median(self.all_prices))}

#TEST        
# url="https://www.olx.pl/mazowieckie/q-huawei-p30/"
# answ=OLXJJ(url).get_all_prices(['galaxy', 'uszkodzony'])
# for x in answ:
#     print(x+" : "+str(answ.get(x)))

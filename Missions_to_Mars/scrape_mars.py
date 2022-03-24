from bs4 import BeautifulSoup
from splinter import Browser
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import requests
import time
import pymongo


client = pymongo.MongoClient('mongodb://localhost:27017')
db = client.mars_db
collection = db.images


dblist = client.list_database_names()

if 'mars_db' in dblist:
    db.drop_collection('images')



url = "https://redplanetscience.com/"

executable_path = {'executable_path': ChromeDriverManager().install()}
browser = Browser('chrome', **executable_path, headless=False)
browser.visit(url)
html = browser.html


news_soup = BeautifulSoup(html, 'html.parser')

news = news_soup.find("div", class_="list_text")
mars_title = news.find("div", class_="content_title")

target_site = 'https://spaceimages-mars.com'
browser.visit(target_site)
html = browser.html
soup = BeautifulSoup(html,'html.parser')
featured_image_url = target_site +"/"+ soup.find('img', class_='headerimage fade-in')['src']
featured_image_title = soup.find('h1', class_="media_feature_title").text.strip()




mars_facts = "https://galaxyfacts-mars.com"
mars_series = pd.read_html(mars_facts)

mars_df = mars_series[1]
mars_df.columns = ['Label', 'Mars']
mars_df.set_index('Label', inplace=True)

mars_df.index.name=None

html_table = mars_df.to_html(index=False, header=False, classes="table table-striped")

hemi_url = 'https://marshemispheres.com'

browser.visit(hemi_url)
hemi_html = browser.html
hemi_soup = BeautifulSoup(hemi_html, "html.parser")
hemi_links = hemi_soup.find("div", class_='collapsible results')

mars_hemispheres = hemi_links.find_all('div', class_='item')


hemisphere_image_urls = []

for i in mars_hemispheres:
    hemisphere = i.find('div', class_="description")
    title = hemisphere.h3.text  
    hemisphere_link = hemisphere.a["href"]    
    browser.visit(hemi_url +"/"+ hemisphere_link)        
    image_html = browser.html
    image_soup = BeautifulSoup(image_html, 'html.parser')        
    image_link = image_soup.find('div', class_='downloads')
    image_url = image_link.find('li').a['href']
    image_dict = {}
    image_dict['title'] = title
    image_dict['img_url'] = hemi_url +"/"+ image_url        
    hemisphere_image_urls.append(image_dict)


browser.back()

browser.quit()


mission_to_mars ={
    'news_title' : nasa_news.get_text(),
	'summary': news_title.get_text(),
    'featured_image_title': featured_image_title,
    'featured_image': featured_image_url,
    'fact_table': html_table,
    'hemisphere_images': hemisphere_image_urls
    }
collection.insert_one(mission_to_mars)

# Dependencies
# from bs4 import BeautifulSoup as bs
# from webdriver_manager.chrome import ChromeDriverManager
# import requests
# import pymongo
# from splinter import Browser
# from flask import Flask, render_template, redirect
# from flask_pymongo import PyMongo
# import pandas as pd

# def init_browser():
#     executable_path = {'executable_path': ChromeDriverManager().install()}
#     browser = Browser('chrome', **executable_path, headless=False)
# def scrape():
#     browser=init_browser()
#     mars_dict={}

#     url = 'https://redplanetscience.com/'
#     browser.visit(url)
#     html=browser.html
#     soup=bs(html,'html.parser')


#     news_title=soup.find_all('div', class_='content_title')[0].text
#     news_p=soup.find_all('div', class_='article_teaser_body')[0].text
    

#     img_url="https://spaceimages-mars.com"
#     browser.visit(img_url)

#     html=browser.html
#     soup=bs(html,"html.parser")
#     image_url=soup.find_all('article')

#     image_url=soup.find('article')['style']
#     image_url=image_url.split("'")[1]

#     featured_image_url=img_url+image_url
    


#     url='https://galaxyfacts-mars.com'
#     tables=pd.read_html(url)
    
#     mars_fact=tables[0]
#     mars_fact=mars_fact.rename(columns={0:"Profile",1:"Value"},errors="raise")
#     mars_fact.set_index("Profile",inplace=True)
#     mars_fact
    
#     fact_table=mars_fact.to_html()
#     fact_table.replace('\n','')
    

#     url='https://marshemispheres.com'
#     browser.visit(url)
#     html=browser.html
#     soup=bs(html,'html.parser')


#     mars_hems=soup.find('div',class_='collapsible results')
#     mars_item=mars_hems.find_all('div',class_='item')
#     hemisphere_image_urls=[]


#     for item in mars_item:
#         try:
#             hem=item.find('div',class_='description')
#             title=hem.h3.text
#             hem_url=hem.a['href']
#             browser.visit(url+hem_url)
#             html=browser.html
#             soup=bs(html,'html.parser')
#             image_src=soup.find('li').a['href']
#             if (title and image_src):
#                 print('-'*50)
#                 print(title)
#                 print(image_src)
#             hem_dict={
#                 'title':title,
#                 'image_url':image_src
#             }
#             hemisphere_image_urls.append(hem_dict)
#         except Exception as e:
#             print(e)

#     mars_dict={
#         "news_title":news_title,
#         "news_p":news_p,
#         "featured_image_url":featured_image_url,
#         "fact_table":fact_table,
#         "hemisphere_images":hemisphere_image_urls
#     }

#     browser.quit()
#     return mars_dict
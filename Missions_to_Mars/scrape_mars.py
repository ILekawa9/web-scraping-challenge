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

print(client.list_database_names())
 
dblist = client.list_database_names()
print(dblist)

if 'mars_db' in dblist:
    print('Database exists')
    db.drop_collection('images')
    print('mars_db dropped')


url = "https://redplanetscience.com/"

executable_path = {'executable_path': ChromeDriverManager().install()}
browser = Browser('chrome', **executable_path, headless=False)
browser.visit(url)
html = browser.html


news_soup = BeautifulSoup(html, 'html.parser')
nasa_news = news_soup.find("div", class_="list_text")
news_title = nasa_news.find("div", class_="content_title")


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

print(hemi_links)


hemisphere_image_urls = []
    # start loop
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
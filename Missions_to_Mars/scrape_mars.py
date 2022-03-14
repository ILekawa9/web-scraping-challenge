from bs4 import BeautifulSoup
from splinter import Browser
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import requests
import time
import pymongo

# set up mongo
# Use PyMongo to establish Mongo connection
client = pymongo.MongoClient('mongodb://localhost:27017')
db = client.mars_db
collection = db.images

# print(client.list_database_names())

# check if database exists if it does, delete it 
dblist = client.list_database_names()
# print(dblist)

if 'mars_db' in dblist:
  #  print('Database exists')
    db.drop_collection('images')
   # print('mars_db dropped')

# news
url = "https://mars.nasa.gov/news/"

executable_path = {'executable_path': ChromeDriverManager().install()}
browser = Browser('chrome', **executable_path, headless=False)
browser.visit(url)
html = browser.html

# Create BeautifulSoup object; parse with 'html.parser'
news_soup = BeautifulSoup(html, 'html.parser')
# news_soup = BeautifulSoup(html, 'lxml')
nasa_news = news_soup.find("div", class_="list_text")
news_title = nasa_news.find("div", class_="content_title")

# find featured image
target_site = 'https://spaceimages-mars.com'
browser.visit(target_site)
html = browser.html
soup = BeautifulSoup(html,'html.parser')
featured_image_url = target_site +"/"+ soup.find('img', class_='headerimage fade-in')['src']
featured_image_title = soup.find('h1', class_="media_feature_title").text.strip()



# mars facts
mars_facts = "https://galaxyfacts-mars.com"
mars_series = pd.read_html(mars_facts)
# There are two tables on this page, read the first one
mars_df = mars_series[1]
mars_df.columns = ['Label', 'Mars']
mars_df.set_index('Label', inplace=True)
#drop index.name to avoid funky second index header row
mars_df.index.name=None
# create html version of pandas table
html_table = mars_df.to_html(index=False, header=False, classes="table table-striped")

hemi_url = 'https://marshemispheres.com'
#parse the landing page, isolate the image links in the item div
browser.visit(hemi_url)
hemi_html = browser.html
hemi_soup = BeautifulSoup(hemi_html, "html.parser")
hemi_links = hemi_soup.find("div", class_='collapsible results')
# collect all items in collapsible resultes container
mars_hemispheres = hemi_links.find_all('div', class_='item')

# print(hemi_links)

# create a list for the names and image links
hemisphere_image_urls = []
    # loop through each hemisphere data
for i in mars_hemispheres:
    # Collect Title
    hemisphere = i.find('div', class_="description")
    title = hemisphere.h3.text  
    # Collect image link by browsing to hemisphere page
    hemisphere_link = hemisphere.a["href"]    
    browser.visit(hemi_url +"/"+ hemisphere_link)        
    image_html = browser.html
    image_soup = BeautifulSoup(image_html, 'html.parser')        
    image_link = image_soup.find('div', class_='downloads')
    image_url = image_link.find('li').a['href']
    # Create Dictionary to store title and url info
    image_dict = {}
    image_dict['title'] = title
    image_dict['img_url'] = hemi_url +"/"+ image_url        
    hemisphere_image_urls.append(image_dict)
    # insert into MongoDB
    # collection.insert_one(image_dict)

browser.back()

browser.quit()

# Return results to MongoDB
mission_to_mars ={
    'news_title' : nasa_news.get_text(),
	'summary': news_title.get_text(),
    'featured_image_title': featured_image_title,
    'featured_image': featured_image_url,
    'fact_table': html_table,
    'hemisphere_images': hemisphere_image_urls
    }
collection.insert_one(mission_to_mars)
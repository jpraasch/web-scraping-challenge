import pymongo
import requests
from splinter import Browser
from bs4 import BeautifulSoup as bs
import pandas as pd
import time


# DB Setup
# 

client = pymongo.MongoClient('mongodb://localhost:27017')
db = client.mars_db
collection = db.mars 


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser('chrome', **executable_path, headless=False)


def scrape():
    browser = init_browser()
    collection.drop()

    # Nasa Mars news
    news_url = 'https://redplanetscience.com/'
    browser.visit(news_url)
    news_html = browser.html
    news_soup = bs(news_html,"html.parser")
    news_title = news_soup.find("div",class_="content_title").text
    news_para = news_soup.find("div", class_="article_teaser_body").text

    # JPL Mars Space Images - Featured Image
    jurl = 'https://spaceimages-mars.com/'
    browser.visit(jurl)
    jhtml = browser.html
    jpl_soup = bs(jhtml,"html.parser")
    image_url = jpl_soup.find("img", class_="headerimage fade-in")["src"]
    featured_image_url = "https://spaceimages-mars.com/" + image_url

    # Mars fact
    murl = 'https://galaxyfacts-mars.com/'
    table = pd.read_html(murl)
    mars_df = table[0]
    marsclean= mars_df.set_axis(["0", "Mars" , "Earth" ], axis=1, inplace=False)
    mars_df2 =  marsclean[['0', 'Mars']]
    mars_fact_html = mars_df2.to_html(header=False, index=False)

    # Mars Hemispheres
    mhurl = 'https://marshemispheres.com/'
    browser.visit(mhurl)  
    mhtml = browser.html 
    mh_soup = bs(mhtml,"html.parser") 
    results = mh_soup.find_all("div",class_='item')
    hemisphere_image_urls = []
    for result in results:
            product_dict = {}
            titles = result.find('h3').text
            end_link = result.find("a")["href"]
            image_link = "https://marshemispheres.com/" + end_link    
            browser.visit(image_link)
            html = browser.html
            soup= bs(html, "html.parser")
            downloads = soup.find("div", class_="downloads")
            image_url = downloads.find("a")["href"]
            product_dict['title']= titles
            product_dict['image_url']= image_url
            hemisphere_image_urls.append(product_dict)








    

    # Close the browser after scraping
    browser.quit()


    # Return results
    mars_data ={
		'news_title' : news_title,
		'summary': news_para,
        'featured_image': featured_image_url,
		'fact_table': mars_fact_html,
		'hemisphere_image_urls': hemisphere_image_urls,
        'news_url': news_url,
        'jpl_url': jurl,
        'fact_url': murl,
        'hemisphere_url': mhurl,
        }
    collection.insert(mars_data)
# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager


def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)
   
    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemi_dict" : mars_hemispheres(browser)
    }

    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


def featured_image(browser):
    # Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

def mars_hemispheres(browser):
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # List to hold the images and titles.
    hemisphere_image_urls = []

    hemi_images = []
    hemi_titles = []

    html = browser.html
    hemisphere_title_soup = soup(html, 'html.parser')
    

    titles = hemisphere_title_soup.find_all('div', class_='description')
    for title in titles:
        title_text = title.find('h3').text
        hemi_titles.append(title_text)

   
    full_image_urls = ["https://astrogeology.usgs.gov/search/map/Mars/Viking/cerberus_enhanced", 
                    "https://astrogeology.usgs.gov/search/map/Mars/Viking/schiaparelli_enhanced",
                    "https://astrogeology.usgs.gov/search/map/Mars/Viking/syrtis_major_enhanced",
                    "https://astrogeology.usgs.gov/search/map/Mars/Viking/valles_marineris_enhanced"
                    ]

    for i in range(len(full_image_urls)):
        url_item = full_image_urls[i]
        browser.visit(url_item)
            
        html = browser.html
        hemisphere_img_soup = soup(html, 'html.parser')
        #print(hemisphere_img_soup)
        
        imgs = hemisphere_img_soup.find('div', class_='wide-image-wrapper')
        #print (imgs)
        f_url = imgs.find("li")
        x = imgs.find("a")["href"]
        hemi_images.append(x)
    #print(len(hemi_images))
   
    
    
    hemisphere_image_urls = []

    for i, j in zip(hemi_titles, hemi_images):
        hemisphere_image_urls.append({"title": i, "image_url": j})


    return hemisphere_image_urls
    
if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())


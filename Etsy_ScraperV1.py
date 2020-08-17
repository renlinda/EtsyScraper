
from bs4 import BeautifulSoup
import requests, csv
import re


def getSoup(link):
    nolink=True #repeat until internet connection works and request goes through
    while nolink:        
        res=requests.get(link) #get html
        try:
            res.raise_for_status()
            nolink=False
        except requests.exceptions.HTTPError:
            pass           
    return BeautifulSoup(res.text,'lxml')

#remove emojis to prevent character errors
def remove_emoji(string):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)
       
master = open('Etsy_Scraped.csv','w', newline= '')
mast = csv.writer(master)
mast.writerow(["listing_id","listing_name","listing_link","display_img","shop_name","price","free_shipping","shop_rating","num_shop_reviews"])
data = {}
count = 0
#replace with your desired link
url = "https://www.etsy.com/ca/search?q=tree%20painting"

#get data in the 69 pages
for i in range(1,70):
    count = count +1
    print(count)
    try:
        if i==1:
            
            link = getSoup(url)
        else:
            link = getSoup(url+"&ref=pagination&page"+str(i))
    except requests.exceptions.SSLError:
        continue
        
    table = link.find("ul","responsive-listing-grid")
    listings = table.find_all("li")
    
    for i in listings:
        listing = i.find("div", class_="js-merch-stash-check-listing")
        data['listing_id'] = listing.get("data-listing-id")
        name = listing.find("a").get("title")
        data['listing_name'] = remove_emoji(name).encode("utf-8")
        shoplink = i.find('a')['href']
        data['listing_link'] = shoplink

        try:
            data['display_img'] = i.find('img')['src']
        except KeyError:
            continue
        
        data['shop_name'] = i.find("div",class_="v2-listing-card__shop").find("p", class_="text-gray-lighter text-body-smaller display-inline-block").text
        
        if  i.find("div",class_="v2-listing-card__shop").find("span",class_="v2-listing-card__rating icon-t-2 display-block").find("span",class_="stars-svg stars-smaller") != None:
            inputTag = i.find("div",class_="v2-listing-card__shop").find("span",class_="v2-listing-card__rating icon-t-2 display-block").find("span",class_="stars-svg stars-smaller").find(attrs={"name": "initial-rating"})
            data["shop_rating"] = inputTag['value']
        
        if i.find("div",class_="v2-listing-card__shop").find("span",class_="v2-listing-card__rating icon-t-2 display-block").find("span",class_="text-body-smaller text-gray-lighter display-inline-block icon-b-1") != None:
            data["num_shop_reviews"] = i.find("div",class_="v2-listing-card__shop").find("span",class_="v2-listing-card__rating icon-t-2 display-block").find("span",class_="text-body-smaller text-gray-lighter display-inline-block icon-b-1").text
        
        if i.find("span",class_="n-listing-card__price text-gray mt-xs-0 strong display-block text-body-larger").find("span",class_="currency-value") != None:
            data["price"] = i.find("span",class_="n-listing-card__price text-gray mt-xs-0 strong display-block text-body-larger").find("span",class_="currency-value").text
        else:
            data["price"] = "Not Given"
     
        if i.find("span", class_="wt-badge wt-badge--small wt-badge--sale-01") != None:
            data["free_shipping"] = ("Yes")
        else:
            data["free_shipping"] = ("No")

        mast.writerow([data['listing_id'],data['listing_name'],data['listing_link'],data['display_img'],data['shop_name'], data["price"],data["free_shipping"],data["shop_rating"],
        data["num_shop_reviews"]])
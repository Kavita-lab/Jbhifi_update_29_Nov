from time import sleep
from datetime import datetime
from requests import get, post
from string import punctuation
from selenium import webdriver
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import logging
import urllib3
import sys

urllib3.disable_warnings()
get_url = "https://tcesffb3s8.execute-api.ap-south-1.amazonaws.com/dev/getinput-jbhifi-office"
post_url = "https://tcesffb3s8.execute-api.ap-south-1.amazonaws.com/dev/sitestats"
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)
l = logging.getLogger("test")


def find_model(name):
    model = None
    model_found = False
    n = name.split()
    for i in n:
        for j in i:
            try:
                j = int(j)
                model_found = True
                model = i
                return model_found, model
            except:
                model = None
    return model_found, model
    

def model_filter(name, model):
    return True if model.lower() in name.lower() else False

#Get product data from API.
def get_data():
    #  For API
    while True:
        data_dict = get(get_url).json()
        if data_dict['responseCode'] == 200:
            break
        else:
            print('Scraping Finished..')
            sleep(4)#Momax Ring Case Compatible with AirTags - Dark Grey

  #  data_dict = {
  #      "responseCode": 200,
  #      "responseMessage": "get scraping data from rabbitmq successfully",
  #      "preferencePojo": {
  #          "preferenceId": 84,
  #          "userId": 1,
  #          "url_scrap": "https://www.jbhifi.com.au/",
  #          "product_scrap": 'Apple iPad Pro 3rd Gen 256GB, Wi-Fi + 5G, 11 in - Space Grey',s
  #          "createdDate": "2021-02-25 05:34:10",
  #          "category": "Mobile",
  #          "sku": "sku",
  #          "price": 99,
  #         "variancepercentage": 0,
  #          "status": 0,
  #          "seller": "Xtreme",
  #          "verified": "Accepted",
  #          "mpn": "0",
  #          "productUrl": "https://www.jbhifi.com.au/products/samsung-galaxy-z-fold3-5g-256gb-black?queryID=7e0ab9bc5db3f886a37636ffbc7694b1&objectID=530597"
            
  #      }
  #  }           
#"productUrl": ""
#514790
#Samsung QN85A 65" Neo QLED 4K Smart TV [2021]
#https://www.becextech.com.au/catalog/surgoi58g256pltprt-p-15926.html#.YPReTOgzZPY
#https://www.harveynorman.com.au/samsung-galaxy-a52-128gb-awesome-black.html
    if data_dict['responseCode'] != 200:
        return False, False, False, False
    prd = data_dict['preferencePojo']

    is_unique_product_search = False
    is_product_url_key_exists = False
    if "productUrl" in prd:
        is_product_url_key_exists = True
    if prd["verified"].lower().strip() == "accepted" and is_product_url_key_exists:
        if prd['productUrl'].strip() != "":
            if prd['url_scrap'] in prd['productUrl'].strip():
                name = prd['productUrl']
                print("scraping using productUrl key {}".format(name))
                is_unique_product_search = True
            else:
                if prd['mpn'].strip() != "":
                    if (prd['mpn'].strip()).isnumeric():
                        num = int(prd['mpn'].strip())
                        if num == 0:
                            name = prd['product_scrap'].strip()
                            print("scraping using product_scrape key {}".format(name))
                        else:
                            name = prd['mpn'].strip()
                            print("scraping using mpn key {}".format(name))
                    else:
                        name = prd['mpn'].strip()
                        print("scraping using mpn key {}".format(name))
                else:
                    name = prd['product_scrap'].strip()
                    print("scraping using product_scrape key {}".format(name))
        elif prd['mpn'].strip() != "":
            if (prd['mpn']).strip().isnumeric():
                num = int(prd['mpn'].strip())
                if num == 0:
                    name = prd['product_scrap'].strip()
                    print("scraping using product_scrape key {}".format(name))
                else:
                    name = prd['mpn'].strip()
                    print("scraping using mpn key {}".format(name))
            else:
                name = prd['mpn'].strip()
                print("scraping using mpn key {}".format(name))
        else:
            name = prd['product_scrap'].strip()
            print("scraping using product_scrape key {}".format(name))
    else:
        if prd['mpn'].strip() != "":
            if (prd['mpn'].strip()).isnumeric():
                num = int(prd['mpn'].strip())
                if num == 0:
                    name = prd['product_scrap'].strip()
                    print("scraping using product_scrape key {}".format(name))
                else:
                    name = prd['mpn'].strip()
                    print("scraping using mpn key {}".format(name))
            else:
                name = prd['mpn'].strip()
                print("scraping using mpn key {}".format(name))
        else:
            name = prd['product_scrap']
            print("scraping using product_scrape key {}".format(name))

    price = prd['price']
    seller = prd['seller']
    return True, name, price, seller, prd, is_unique_product_search


def post_data(data_list, min_price, competition, comp_price, time, url, prd):
    response = None
    uploaded = False
    upload = ''
    for data in data_list:
        try:
            sku = data['sku']
        except Exception as e:
            n = e
            sku = 'SKU not available'
        sub = {
            "siteUrl": url,
            "productName": data['name'],
            "preferenceId": prd['preferenceId'],
            "minPrice": min_price,
            "userPrice": prd['price'],
            "competitionPrice": comp_price,
            "seller": data['merchant'],
            "processing_time": data['time'] + time,
            "competionName": competition,
            "productUrl": data['url'],
            "sku": sku,
        }
        
        # For API
        # while True:
        #     try:
        #         response = post(post_url, json=sub)
        #         if response.status_code == 200:
        #             break
        #     except:
        #         print('Can\'t post data retrying in 3 seconds')
        #         sleep(3)
        if float(data['price']) == float(comp_price) and not uploaded:
            if not sub['sku']:
                sub["sku"] = get_sku(data['url'])
            response = post(post_url, json=sub)
            upload = sub
            uploaded = True
        # For Manual
        l.critical(f"{sub['productName']}\n user price: {sub['userPrice']}, min price: {sub['minPrice']}, comp price: {sub['competitionPrice']} actual price: {data['price']}\n")
    l.critical(f'{upload}')
    print(f'\n\nuploaded data:-\n{upload}\n\n')
    sleep(5)
    return response

def get_sku(url):
    l.critical(url)
    browser = webdriver.Firefox()
    # browser.minimize_window()
    browser.get(url)
    sku = 'SKU name not available'
    try:
        if 'binglee' in url:
            try:
                sku = browser.find_elements_by_css_selector('.product-highlight>li')[0].text.split(' ')[-1]
            except Exception as e:
                n = e
        if 'officeworks' in url:
            try:
                sku = browser.find_element_by_id('product-code').text
            except Exception as e:
                n = e

        if 'jbhifi' in url:
            try:
                sku = browser.find_elements_by_css_selector('.product-meta.prod-code>dd')[1].text
            except Exception as e:
                n = e

    except Exception as e:
        n = e

    browser.quit()
    return sku

def calculate_price(data_list, price):
    price_list = []
    merchant_price_list = []
    min_price = float(0)
    user_price = float(price)
    comp_price = float(0)
    merchant = 'Seller name not available'
    try:
        #get price_list and merchant_price_list
        for details in data_list:
            if details['price'] != 0:
                price_list.append(float(details['price']))
                merchant_price_list.append((details['merchant'], float(details['price'])))
        #get the minimum price list in price collection.
        if len(price_list)>0:
            price_list.sort()
            min_price = price_list[0]
            # get competitive price
            if min_price < user_price:
                comp_price = min_price
            else:
                comp_price = user_price
        else:
            min_price = float(0)
            comp_price = user_price

        #get the merchant details
        if len(merchant_price_list) >0:
            for merchant_name, mc_price in merchant_price_list:
                if mc_price == comp_price:
                    merchant = merchant_name
                break
    except Exception as ex:
        print(ex)
    return min_price, merchant, comp_price

def calculate(data_list, price):
    p_l = []
    m_l = []
    min_price = '0'
    comp_price = '0'
    comp = 'Seller name not available'
    for i in data_list:
        if i['price'] != '0':
            p_l.append(i['price'])
            m_l.append((i['merchant'], i['price']))
    try:
        p_l.sort()
        min_price = p_l[0]
        for i in m_l:
            if i[0] == min_price:
                comp = i[1]
                break
            else:
                comp = 'Seller name not available'
    except Exception as e:
        l.critical(e)

    try:
        m_p = min_price if float(price) >= float(min_price) else price
    except Exception as e:
        l.critical(e)
        m_p = min_price

    for i in m_l:
        if i[1] == min_price:
            comp_price = i[1]
            comp = i[0]
            break

    return m_p, comp, comp_price


def clean_text(string: str):
    text = ''
    for char in string:
        if char not in punctuation.replace('()', '').replace('&', ''):
            text = text + char
    return text


def clean_price(string: str):
    price = ''
    acceptable = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '.']
    for char in string:
        if char in acceptable:
            price = price + char

    p = price.split('.')
    if len(p) <= 2:
        return price
    else:
        main_price = f'{p[0]}.{p[1]}'
        return clean_price(main_price)


def sort_price(data_list: list):
    price_list = [n['price'] for n in data_list]
    try:
        price_list.sort(reverse=False)
    except Exception as e:
        error = e
    data_sorted = []
    for price in price_list:
        for single_data in data_list:
            if single_data['price'] == price and single_data not in data_sorted:
                data_sorted.append(single_data)

    return data_sorted


class Compare:
    @staticmethod
    def clean_text(given_string: str):
        text = ''.join([word for word in given_string if word not in punctuation])
        text = text.lower()
        return text

    @staticmethod
    def cosine_sim_vectors(vec1, vec2):
        vec1 = vec1.reshape(1, -1)
        vec2 = vec2.reshape(1, -1)

        return cosine_similarity(vec1, vec2)[0][0]

    def filter(self, main_string: str, to_compare: list, given_filter: float):
        t1 = datetime.now()
        #l.critical(f'{len(to_compare)} Data Found')
        #print(f'{len(to_compare)} Data Found', end=' ')
        words = []
        for i in to_compare:
            words.append(i['name'])

        words.append(main_string)
        cleaned = list(map(self.clean_text, words))
        vectorized = CountVectorizer().fit_transform(cleaned)
        vector = vectorized.toarray()
        original = vector[-1]
        products = vector[:-1]
        filtered = []
        n = 0
        for product in products:
            similarity = self.cosine_sim_vectors(product, original)
            if similarity >= given_filter:
                filtered.append(to_compare[n])
            n += 1
        ret_data = []
        for i in to_compare:
            for j in filtered:
                if i == j:
                    ret_data.append(i)
        l.critical(f'{len(ret_data)} will be uploaded..')
        return sort_price(ret_data), (datetime.now() - t1).total_seconds() / len(to_compare)

from selenium import webdriver
from datetime import datetime
import time
from Functions import clean_text, clean_price
import logging
import sys
import urllib
import urllib3

urllib3.disable_warnings()
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)
l = logging.getLogger("test")

def scrap(given_name: str, given_url, given_model_no=None, is_unique_product_search=False, product_details = None):
    """
    :param given_model_no:
    :param given_name:
    :param given_url:
    :return: List of Scraped data, Data error count and Keyword
    """
    is_product_url_key_exists = False
    if "productUrl" in product_details:
        is_product_url_key_exists = True

    browser = webdriver.Firefox()
#    browser.minimize_window()

    #inp_name = given_name.replace(' ', '+').lower()
    data_list = []
    #search_url = given_url.replace('{}', inp_name)
    if is_product_url_key_exists:
        if given_name != product_details['productUrl']:
            inp_name = urllib.parse.quote_plus(given_name)
            search_url = given_url.format(inp_name)
        else:
            search_url = given_name
    else:
        inp_name = urllib.parse.quote_plus(given_name)
        search_url = given_url.format(inp_name)

    browser.get(search_url)

    try:
        page_404_error = browser.find_elements_by_css_selector("h1")[1].text

    except:
        page_404_error = ""
    if page_404_error.strip().lower() == "sorry!":
        print("{}  Url is invalid.".format(search_url))
        is_unique_product_search = False
        if given_name == product_details['product_scrap'].strip():
            browser.quit()
            return data_list
        if given_name == product_details['mpn'].strip():
            is_mpn_valid = False
        else:
            is_mpn_valid = True

        if product_details['mpn'].strip() != "" and given_name != product_details['product_scrap'].strip():   #and is_mpn_valid

            if is_mpn_valid:
                if (product_details['mpn'].strip()).isnumeric():
                    num = int(product_details['mpn'].strip())
                    if num == 0:
                        name = product_details['product_scrap'].strip()
                        print("scraping using product_scrape key {}".format(name))
                    else:
                        name = product_details['mpn'].strip()
                        print("scraping using mpn key {}".format(name))
                else:
                    name = product_details['mpn'].strip()
                    print("scraping using mpn key {}".format(name))
                is_mpn_valid = False
            else:
                name = product_details['product_scrap'].strip()
                if given_name != name:
                    print("scraping using product_scrape key {}".format(name))
            given_name = name
            browser.quit()
            data_list = scrap(given_name, given_url, given_model_no, is_unique_product_search, product_details)

        else:
            name = product_details['product_scrap'].strip()
            if given_name != name:
                print("scraping using product_scrape key {}".format(name))
            given_name = name
            browser.quit()
            data_list = scrap(given_name, given_url, given_model_no, is_unique_product_search, product_details)


        return data_list
    else:
        try:
            no_results = browser.find_elements_by_css_selector("div[data-ref=\"search-no-results\"]")[0].text
        except:
            no_results = ""
        if no_results != "":
            #go for next search
            browser.quit()
            return data_list
        else:
            try:
                search_results = browser.find_elements_by_css_selector("div[data-sectionid=\"nbHits\"]")[0].text
            except:
                search_results = ""
            if search_results != "" :
                #code for searching page.
                items = browser.find_elements_by_css_selector('.sc-bdVaJa.Tile-iqbpf7-0.fIkVYO')
                l.info(f'{len(items)} Results Found for: {given_name}')
            else:
                #code for individual page.
                try:
                    t1 = datetime.now()

                    try:
                        title = clean_text(browser.find_elements_by_css_selector("h1[data-ref=\"product-title\"]")[0].text)
                        if is_product_url_key_exists:
                            url = product_details['productUrl'].strip()
                        else:
                            url = ""
                        # print(title)
                    except IndexError:
                        pass

                    try:
                        p = browser.find_elements_by_css_selector("span[data-ref=\"product-price-isNotRR\"]")[0].text
                        prd_price = clean_price(p)
                        # if prd_price == '':
                        #     a = [][2]
                    except IndexError:
                        p = browser.find_elements_by_css_selector("span[data-ref=\"product-price-isNotRR\"]")[0].text
                        prd_price = clean_price(p)
                    except Exception as e:
                        print(f'\n{e} price\n{title}\n\n')
                        prd_price = '0'

                    try:
                        merchant = clean_text(browser.find_elements_by_css_selector('.get_merchant')[0].text)
                    except Exception as e:
                        n = e
                        # print(f'\n\n{e} marchant \n{title}\n\n')
                        merchant = 'Seller name not available'

                    try:
                        product_code = clean_text(browser.find_elements_by_css_selector("span[data-ref=\"product-code\"]")[0].text)
                    except Exception as e:
                        n = e
                        # print(f'\n\n{e} marchant \n{title}\n\n')
                        product_code = 'product code is not available'

                    timestamp = datetime.now()
                    main = {
                        'name': title,
                        'price': prd_price,
                        'timestamp': timestamp,
                        'merchant': merchant,
                        'time': (datetime.now() - t1).total_seconds(),
                        'url': url,
                        'sku': product_code,
                    }
                    data_list.append(main)
                except AttributeError:
                    pass
                except Exception as e:
                    print(e, end=' AT GET DATA')
                browser.quit()
                return data_list


    for prd_data in items:
        try:
            t1 = datetime.now()

            try:
                title = clean_text(prd_data.find_elements_by_css_selector('.DefaultProductTile__ProductName-dfe2sm-1'
                                                                          '.dRgJNf')[0].text)
                url = prd_data.find_elements_by_css_selector('a')[0].get_attribute('href')
                # print(title)
            except IndexError:
                continue

            try:
                p = prd_data.find_elements_by_css_selector('.ProductPrice__Wrapper-sc-1ye3dgu-0.guXOLt')[0].text
                prd_price = clean_price(p)
                if prd_price == '':
                    a = [][2]
            except IndexError:
                p = prd_data.find_elements_by_css_selector('.ProductPrice__Wrapper-sc-1ye3dgu-0.guXOLt')[0].text
                prd_price = clean_price(p)
            except Exception as e:
                print(f'\n{e} price\n{title}\n\n')
                prd_price = '0'

            try:
                merchant = clean_text(prd_data.find_elements_by_css_selector('.get_merchant')[0].text)
            except Exception as e:
                n = e
                # print(f'\n\n{e} marchant \n{title}\n\n')
                merchant = 'Seller name not available'

            timestamp = datetime.now()
            main = {
                'name': title,
                'price': prd_price,
                'timestamp': timestamp,
                'merchant': merchant,
                'time': (datetime.now() - t1).total_seconds(),
                'url': url,
                'sku': False,
            }
            data_list.append(main)
        except AttributeError:
            pass
        except Exception as e:
            print(e, end=' AT GET DATA')
    try:
        browser.quit()
    except Exception as e:
        print(e)
        pass
    return data_list


def run(name, given_url, given_model_no=None, is_unique_product_search=False, product_details = None):

    data = scrap(name, given_url, given_model_no, is_unique_product_search, product_details)

    return data

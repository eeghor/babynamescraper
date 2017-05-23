from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import pandas as pd
from collections import namedtuple, defaultdict

def get_available_pages():

    available_pages = []

    for a in driver.find_elements_by_xpath("//section[@class='pagination']/ul/li//a[@href]"):
        if a.text.strip().isdigit():
            available_pages.append(int(a.text.strip()))

    current_page = int(driver.find_element_by_xpath("//section[@class='pagination']/ul/li[@class='current']//a[@href]").text.strip())

    return (current_page, available_pages)

name_rec = namedtuple("name_rec", "name gender ethnicity")

if __name__ == "__main__":

    lst_names = []

    driver = webdriver.Chrome("C:\\Users\igork\PycharmProjects\ethnicname-scraper\webdriver\chromedriver.exe")

    start_page = "http://www.babynames.net/categories"

    t0 = time.time()

    driver.get(start_page)
    driver.implicitly_wait(60)

    # category urls
    cat_urls = defaultdict(str)

    while True:

        # find the Next button
        nxt_btn = driver.find_element_by_partial_link_text("Next")

        # see what page numbers available for pagination

        current_page, available_pages = get_available_pages()
        max_avail_page = max(available_pages)

        for a in driver.find_elements_by_xpath("//ul[contains(@class, 'names-results') and contains(@class, 'category-view')]/li/a[@href]"):

            try:
                namekind_name = a.find_element_by_xpath("span")
            except:
                print("no next button here.. skipping..")
                break   # now have to press a button to move to the next page

            cat_urls[namekind_name.text.strip().lower()] = a.get_attribute("href")

        # collected letter urls on this page, go to the next page

        if (current_page == max_avail_page) and ("void" in nxt_btn.get_attribute("href")):
            break
        else:
            nxt_btn.click()
            time.sleep(3)

    print("collected {} letter urls".format(len(cat_urls)))

    # now start visiting the letter pages
    for l in cat_urls:

        print("scraping category {}...".format(l.upper()))

        driver.get(cat_urls[l])

        while True:

            # find the Next button
            try:
                nxt_btn = driver.find_element_by_partial_link_text("Next")
            except:
                break

            current_page, available_pages = get_available_pages()
            max_avail_page = max(available_pages)

            for gnd_elem, nam_elem in zip(driver.find_elements_by_xpath("//ul[contains(@class, 'names-results') and contains(@class, 'listing-view')]/li/a[@href]/span[contains(@class, 'result-gender')]"),
                         driver.find_elements_by_xpath("//ul[contains(@class, 'names-results') and contains(@class, 'listing-view')]/li/a[@href]/span[contains(@class, 'result-name')]")):

                gender = gnd_elem.get_attribute("class").split()[-1].strip()
                name = nam_elem.text.strip().lower()

                lst_names.append(name_rec(name=name, gender=gender, ethnicity=l))

            if (current_page == max_avail_page) and ("void" in nxt_btn.get_attribute("href")):
                break
            else:
                nxt_btn.click()
                time.sleep(3)

    driver.close()

    print("done. collected {} names. elapsed time: {:.0f} min {:.0f} sec".format(len(lst_names),
                                                                                 *divmod(time.time() - t0, 60)))
    df = pd.DataFrame(lst_names, columns=lst_names[0]._fields)
    df.to_csv("names_by_ethnicity.txt", index=False)
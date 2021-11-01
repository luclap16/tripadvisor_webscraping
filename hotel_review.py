from selenium import webdriver
import time
from bs4 import BeautifulSoup as soup
import csv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

elements = {
        'hotel_rate': 'bvcwU P',
        'hotel_rate_string': 'cNJsa',
        'hotel_class': 'TkRkB d H0',
        'hotel_aspects': 'cmZRz f',
        'username': 'ui_header_link bPvDb',
        'user_rate': 'location-review-review-list-parts-RatingLine__bubbles--GcJvM',
        'review_title': 'fpMxB MC _S b S6 H5 _a',
        'review_text': 'XllAv H4 _a',
        'date_of_stay': 'euPKI _R Me S4 H3',
        'review_helpfulness_vote': 'ekLsQ S2 H2 Ch bzShB',
        'trip_type': 'eHSjO _R Me',
        'review_aspects': 'fFwef S2 H2 cUidx',
        'reviews_next_button': '//a[@class="ui_button nav next primary "]',
        'reviews': 'cWwQK MC R2 Gi z Z BB dXjiy',
        'hotel_name': 'HEADING',
        'hotel_about': 'ABOUT_TAB',
        'read_more_button': '//span[@class="eljVo _S Z"]',
        'hotels_button': '//span[@class="ui_icon hotels brand-quick-links-QuickLinkTileItem__icon--2iguo"]',
        'hotels_button_2': '//*[@id="lithium-root"]/main/div[1]/div[2]/div/div/div[1]/a',
        'city_search_input': '/html/body/div[2]/div/form/input[1]',
        'hotels_in_city': '//a[@class="property_title prominent "]',
        'close_pop_up': '//div[@class="ui_close_x"]',
        'about_tab': '/html/body/div[2]/div[2]/div[2]/div[4]/div/div[1]/div[4]/div/div/div/div'
}
elements['review-class'] = 'review-container'

#def extension
def getPageSoup(driver):
    page_source = driver.page_source
    page_soup = soup(page_source, 'html.parser')
    return page_soup

def writeInCSV(row):
    global writer
    writer.writerow(row)

def goToCityHotelsPage(city, driver):
     #click on hotels section
    try:
        hotels_button = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, elements['hotels_button'])))
    except TimeoutException:
        hotels_button = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, elements['hotels_button_2'])))
        
    hotels_button.click()
    time.sleep(2)
    
    #search hotels by city's name
    input_city = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, elements['city_search_input'])))
    input_city.send_keys(city)
    input_city.send_keys(Keys.ENTER)

    #close alert if it's visible
    try:
        WebDriverWait(driver, 3).until(EC.alert_is_present(),
                                       'Timed out waiting for PA creation ' +
                                       'confirmation popup to appear.')
        alert = driver.switch_to.alert
        alert.accept()
        print("alert accepted")
    except TimeoutException:
        print("no alert")
        
    #ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    input_city.send_keys(Keys.ENTER)

def clickOnHotelsLink(hotels, driver):
    #define actions for holding a button
    action_key_down_control = ActionChains(driver).key_down(Keys.CONTROL)
    action_key_up_control = ActionChains(driver).key_up(Keys.CONTROL)
    for hotel in hotels:
        if hotel.text not in processed_hotels:
            # print(hotel.text)
            action_key_down_control.perform()
            hotel.click()
            processed_hotels.append(hotel.text)
            action_key_up_control.perform()
            print(processed_hotels)
            break
        else: 
            continue
    time.sleep(10)

def processHotelAspects(aspects):
    for aspect in aspects:
        aspect_name = aspect.div.text.strip()
        aspect_rate = int(aspect.span["class"][1].split("_")[1])/10
        for hotel_aspect in hotel_aspects:
            if hotel_aspect["aspect"] == aspect_name:
                hotel_aspect["rating"] = aspect_rate
    data_row.extend([hotel_aspects[0]["rating"], hotel_aspects[1]["rating"], hotel_aspects[2]["rating"]]) 

def processHotelAbouts(hotel_about_tab):
    hotel_rate = hotel_about_tab.find("span",{"class": elements['hotel_rate']}).text.strip()
    hotel_rate_string = hotel_about_tab.find("div", {"class": elements['hotel_rate_string']}).text.strip()
    print(hotel_rate)
    print(hotel_rate_string)
    try:
            # hotel_class = int(hotel_about.find("div", {"class": elements['hotel_class']}).span["class"][1].split("_")[1])/10
            hotel_class = hotel_about_tab.find("svg",{"class": elements["hotel_class"]})["title"].split(" ")[0]
    except Exception:
            hotel_class = ''
    data_row.extend([hotel_class, hotel_rate, hotel_rate_string])
    print('hotel class: '+hotel_class)
    
    try:
        aspects = hotel_about_tab.findAll("div", {"class": elements['hotel_aspects']})
        
        processHotelAspects(aspects)
    except Exception:
        processHotelAspects([])
        pass

# def reviews_next():
#         try:
#                 reviews_next_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, elements['reviews_next_button'])))
#                 # read_more_button = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH, '//span[@class= "eljVo _S Z"]')))
#         except TimeoutException:
#                 reviews_next_button = ''
#         time.sleep(5)

def clickOnReadMores(driver):
    while True:
        # ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
        # read_more_button = WebDriverWait(driver, 10,ignored_exceptions=ignored_exceptions)\
        #                 .until(EC.presence_of_element_located((By.XPATH, elements['read_more_button'])))
        try:
            read_more_button = WebDriverWait(driver,25).until(EC.element_to_be_clickable((By.XPATH, elements['read_more_button'])))
        except TimeoutException:
            break
        try:
            read_more_button.click()
        except:
            pass
        try:
            read_more_button = WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.XPATH, elements['read_more_button'])))
        except TimeoutException:
            break
        print(read_more_button)
        read_more_button.click()
        time.sleep(2)
        print('Done click read more')
    
    # # try:
    # read_more_button = WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.XPATH, elements['read_more_button'])))
    # # except TimeoutException:
    # #     break #loi
    
    # # try:
    # #     reviews_next_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, elements['reviews_next_button'])))
    # #     # read_more_button = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH, '//span[@class= "eljVo _S Z"]')))
    # # except TimeoutException:
    # #         reviews_next_button = ''
    # # time.sleep(5)

    # print(read_more_button)
    # read_more_button.click()
    # time.sleep(2)

def processReview(review):
    trip_type = 'not mentioned'
    user = review.find("a",{"class": 'ui_header_link bPvDb'}).text.strip()
    print(user)
    user_rate =int(review.find("span", {"class": 'ui_bubble_rating'})["class"][1].split("_")[1])/10
    # print(user_rate)
    review_title = review.find("div", {"class": elements['review_title']}).a.span.text.strip()
    # print(review_title)
    review_text = review.find("q", {"class": elements['review_text']}).span.text
    # print(review_text)
    try:
        date_of_stay = review.find("span", {"class": elements['date_of_stay']}).text.split(":")[1].strip()
    except Exception:
        date_of_stay = ' '
    # print(date_of_stay)
    try:
        review_helpfulness_vote = review.find("span",{"class": elements['review_helpfulness_vote']}).text.strip()
    except Exception:
        review_helpfulness_vote = 0
    # print(review_helpfulness_vote)
    try:
        trip_type = review.find("span", {"class": elements['trip_type']}).text.split(":")[1].strip()
    except Exception:
        pass
    for review_aspect in review_hotel_aspects:
        review_aspect["rating"] = -1
    try:
        aspects = review.findAll("div", {"class": elements['review_aspects']})
        for aspect in aspects:
            aspect_name = aspect.text.strip()
            aspect_rating = int(aspect.span.span["class"][1].split("_")[1])/10
            for review_aspect in review_hotel_aspects:
                if review_aspect["aspect"] == aspect_name:
                    review_aspect["rating"] = aspect_rating
    except Exception as e:
        print(e)
        pass
    data_row.extend((user,review_title,review_text,date_of_stay,user_rate,review_helpfulness_vote,trip_type,review_hotel_aspects[0]["rating"], review_hotel_aspects[1]["rating"], review_hotel_aspects[2]["rating"], review_hotel_aspects[3]["rating"], review_hotel_aspects[4]["rating"], review_hotel_aspects[5]["rating"]))

def processHotel(page_soup, driver):
    global reviews_processed_num
    
    data_row.clear()

    hotel_name = page_soup.find(id= {elements['hotel_name']}).text.strip()
    hotel_about_tab = page_soup.find(id= elements['hotel_about'])
    print(hotel_name)
    data_row.append(hotel_name)
    print(data_row)

    #scrap about section
    processHotelAbouts(hotel_about_tab)

    # here come back
    try:
        reviews_next_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, elements['reviews_next_button'])))
        # think again cmt or not?
        # read_more_button = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH, '//span[@class= "hotels-review-list-parts-ExpandableReview__cta--3U9OU"]')))
    except TimeoutException:
        reviews_next_button = ''
    time.sleep(5)

    #while next button is enabled
    while reviews_next_button != None:
        # href_data = reviews_next_button.get_attribute('href')
        # if href_data is None:
        #     clickOnReadMores(driver)
        # else:
        #     print('Not the first page')
        clickOnReadMores(driver)
        page_soup = getPageSoup(driver)
        reviews = page_soup.findAll("div", {"class": elements['reviews']}) #sua
        print("reviews number: ", len(reviews))

        for review in reviews:
            processReview(review)
            writeInCSV(data_row)
            reviews_processed_num+=1
            if reviews_needed <= reviews_processed_num:
                break
            del data_row[7:]
        if reviews_needed <= reviews_processed_num:
            break
        time.sleep(3)

        # next button
        try:
            reviews_next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, elements['reviews_next_button'])))
            reviews_next_button.click()
            reviews_next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, elements['reviews_next_button'])))
        except TimeoutException:
            break

def processBrowserTabs(driver, parentGUID):
    global elements

    # get the All the session id of the browsers
    allGUID = driver.window_handles
    print(allGUID)

    for guid in allGUID:
    	#if the GUID is not equal to parent window's GUID
        if(guid != parentGUID):
            #switch to the guid #focus on the new tab
            driver.switch_to.window(guid)
            
            # again?
            try:
                WebDriverWait(driver,15).until(EC.presence_of_all_elements_located((By.XPATH,elements['about_tab']))) #kh dùng id ABOUT_TAB vì trùng
            except TimeoutException:
                break
            page_soup = getPageSoup(driver)
            print(page_soup.title.text)

            #process the Hotel
            processHotel(page_soup, driver)
            # except TimeoutException:
            #     pass
            
            # close the tab
            driver.close()
            # switch back to the parent window
            driver.switch_to.window(parentGUID)
            
            print(reviews_processed_num)
            try: 
                close_pop_up = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, elements['close_pop_up'])))
                close_pop_up.click()
                time.sleep(3)
            except TimeoutException:
                pass
        if reviews_needed <= reviews_processed_num:
            break

def main():
    global reviews_needed
    hotels_clicked = 0
    
    #initialize browser's driver
    driver = webdriver.Edge(executable_path = 'C:\\Users\\DELL\\msedgedriver.exe')
    driver.get(URL)
    driver.maximize_window()
    print('- Done. Create new broswer')

    #get input
    city = input("Enter city: ")
    reviews_needed = int(input("Enter number of reviews: "))
    
    goToCityHotelsPage(city, driver)
    
    #close alert if it's visible
    try:
        WebDriverWait(driver, 3).until(EC.alert_is_present(),
                                       'Timed out waiting for PA creation ' +
                                       'confirmation popup to appear.')
        alert = driver.switch_to.alert
        alert.accept()
        print("alert accepted")
    except TimeoutException:
        print("no alert")

    #open tabs for every hotel in the city's page
    hotels = WebDriverWait(driver,15).until(EC.presence_of_all_elements_located((By.XPATH, elements['hotels_in_city'])))
    hotels_in_page = len(hotels)
    print('Hotels in the page: {}'.format(hotels_in_page))
    ActionChains(driver).send_keys(Keys.ESCAPE).perform() #close the Home

    # get the Session id of the Parent
    parentGUID = driver.current_window_handle

    while hotels_clicked <= hotels_in_page:
        clickOnHotelsLink(hotels, driver)
        hotels_clicked += 1
        processBrowserTabs(driver, parentGUID)
        if reviews_needed <= reviews_processed_num:
            break
        hotels = WebDriverWait(driver,15).until(EC.presence_of_all_elements_located((By.XPATH, elements['hotels_in_city'])))
    
    print("Scrap Completed")
    driver.close()
    f.close()

review_hotel_aspects =[{"aspect":"Value", "rating": -1}, {"aspect":"Location", "rating": -1} , {"aspect":"Cleanliness", "rating": -1}, {"aspect":"Service", "rating": -1}, {"aspect":"Rooms", "rating": -1}, {"aspect":"Sleep Quality", "rating": -1}]
hotel_aspects =[ {"aspect":"Location", "rating": -1}, {"aspect":"Cleanliness", "rating": -1}, {"aspect":"Service", "rating": -1}]
header_row = ["Hotel Name", "Hotel Class", "Hotel Rating", "Hotel Quality", hotel_aspects[0]["aspect"], hotel_aspects[1]["aspect"], hotel_aspects[2]["aspect"], "User Name", "Review Title", "Review Text",
                  "Date of Stay", "User Rating", "Review Likes", "Trip Type", review_hotel_aspects[0]["aspect"],
                  review_hotel_aspects[1]["aspect"],review_hotel_aspects[2]["aspect"],review_hotel_aspects[3]["aspect"],
                  review_hotel_aspects[4]["aspect"], review_hotel_aspects[5]["aspect"]] 
data_row = []
reviews_needed = 0
reviews_processed_num = 0
processed_hotels = [] 

f = open('hotels_reviews.csv', 'a', newline='', encoding="utf-8")
writer = csv.writer(f)

writeInCSV(header_row)

URL = "https://www.tripadvisor.com/"

main()
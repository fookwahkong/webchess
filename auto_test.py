import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time


def main():
    os.system('python web.py &')
    #   os.popen('python web.py')

    time.sleep(2)
    print('\n\npaste the link near the place with open new tab')
    print('e.g. https://webchess-1.pohanson.repl.co')
    url = input('Url of web: ')

    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(15)
    driver.get(url)

    print(driver.title)
    driver.find_element_by_xpath("//form//input[@type='submit']").click()

    def move(moves: list):
        """
      give the list moves as a string like how you would input it
      
      e.g. ['51 52', '46 45', '11 12']
      """
        for move in moves:
            move_box = driver.find_element_by_name('move')
            print(move)
            move_box.send_keys(move)
            move_box.submit()
            time.sleep(1.5)

    def fool_mate():
        move(['51 52', '46 45', '61 63', '37 73'])

    def promotion():
        move([
            '01 03', '16 14', '03 14', '17 25', '14 15', '06 05', '15 16', '05 04', '16 17'])
        time.sleep(5)
        move(['q'])
    # fool_mate()
    promotion()


main()
time.sleep(300)

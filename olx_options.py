from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep
from datetime import date


def get_price():
    while True:
        try:
            price_1 = int(input('Enter low-price (integer): '))
            price_2 = int(input('Enter high-price (integer): '))
        except ValueError:
            print('Price must be an integer.')
            continue
        else:
            return price_1, price_2


def olx_filtration(drive: webdriver):
    rang = get_price()

    # Actions with filter feature (price range assignment,
    price_from = drive.find_element(By.CSS_SELECTOR, 'input[name="range-from-input"]')
    price_to = drive.find_element(By.CSS_SELECTOR, 'input[name="range-to-input"]')
    # print(price_from)

    price_from.send_keys(rang[0])
    price_from.send_keys(Keys.ENTER)
    sleep(2)
    price_to.send_keys(rang[1])
    price_to.send_keys(Keys.ENTER)
    sleep(2)


def olx_sorting(drive: webdriver):
    way = input('Enter your wish by how you want to sort (Low / High / New): ')

    # Actions with sorting feature (set from low to high price)
    sort_by_price = drive.find_element(By.CSS_SELECTOR, 'button[aria-describedby="filters.sort"]')
    sort_by_price.click()
    sleep(1)
    if way.capitalize().strip() == 'Low':
        low_price = drive.find_element(By.CSS_SELECTOR, 'button[id="sorting-option-2"]')
        low_price.click()
        sleep(2)
    elif way.capitalize().strip() == 'High':
        high_price = drive.find_element(By.CSS_SELECTOR, 'button[id="sorting-option-3"]')
        high_price.click()
        sleep(2)
    elif way.capitalize().strip() == 'New':
        new_prod = drive.find_element(By.CSS_SELECTOR, 'button[id="sorting-option-1"]')
        new_prod.click()
        sleep(2)
    else:
        print('This option is not available!')
        recommend = drive.find_element(By.CSS_SELECTOR, 'button[id="sorting-option-0"]')
        recommend.click()


def translate_date(s):
    month_names = {
                    'січ': '01', 'лют': '02', 'бер': '03', 'кві': '04', 'тра': '05',
                    'чер': '06', 'лип': '07', 'сер': '08', 'вер': '09', 'жов': '10',
                    'лис': '11', 'гру': '12'
                   }
    if 'сьогодні' in s or 'Cьогодні' in s:
        current = date.today()
        return f'{current.year}-{current.month}-{current.day}'

    post = s.split()[1:4]
    day, month, year = post[0], month_names[post[1][:3]], post[2]
    return f'{year}-{month}-{day}'



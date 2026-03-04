from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from time import sleep
from datetime import date
import asyncio
import mysql.connector

from olx_options import get_price, olx_filtration, olx_sorting, translate_date


def create_table(**kwargs):
    """
        Function for connecting to the DB of MySQL and create table with electronic products
        Parameters:

            table_name: str. Name of the table which will be created.

            **kwargs: Keyword arguments to connect to MySQL DB.
                host - Your host address
                user - Your username of MySQL
                password - Your password of MySQL
                db - Name of MySQL DB
        :return: connection data
    """


    try:
        db = mysql.connector.connect(
            host=kwargs.get('host'),
            user=kwargs.get('user'),
            password=kwargs.get('password'),
            database=kwargs.get('db'),
        )
    except mysql.connector.Error as err:
        print('Problem with connecting to database. Please, check if database exists and data is valid and try again.')
    else:
        curs = db.cursor()

        curs.execute(
            '''
            CREATE TABLE IF NOT EXISTS articles (
            ID INT PRIMARY KEY AUTO_INCREMENT,
            PostLink VARCHAR(255) NOT NULL UNIQUE,
            UserName VARCHAR(255) NOT NULL,
            UserLink VARCHAR(255) NOT NULL,
            PostID INT NOT NULL UNIQUE,
            Title VARCHAR(255) NOT NULL UNIQUE,
            ProductPrice FLOAT NOT NULL,
            PostDate DATE NOT NULL);
            ''')

        db.commit()
        return db



def get_drive() -> webdriver:
    """
        Function allow you to choose which browser to use.
        return: webdriver
    """

    option = Options()
    option.add_experimental_option("detach", True)

    driver = None
    while True:
        browser = input('Choose your browser: \n1. Chrome\n2. Microsoft Edge\n3. Safari\n4. Firefox\n5. Other\n')
        if browser == '1':
            driver = webdriver.Chrome(options=option)
            break
        elif browser == '2':
            driver = webdriver.Edge(options=option)
            break
        elif browser == '3':
            driver = webdriver.Safari(options=option)
            break
        elif browser == '4':
            driver = webdriver.Firefox(options=option)
            break
        elif browser == '5':
            print('Sorry, currently other browsers are not supported!')
            continue
        else:
            print('Sorry, I don\'t understand your choice!')
            continue
    return driver


# Attempt to get data from Rozetka.com via changing script behavior to a more "human" behavior

# def web_process(url, req, filt=False, sorting=False):
#     drive = get_drive()
#     drive.get(url)
#     time.sleep(3)

    # time.sleep(10)
    #
    # body = drive.find_element(By.TAG_NAME, 'body')
    # for _ in range(10):
    #     body.send_keys(Keys.ARROW_DOWN)
    #     time.sleep(0.3)
    # time.sleep(10000)
    #
    # promo = drive.find_element(By.CSS_SELECTOR, 'span[class="exponea-close-cross"')
    # ActionChains(drive).move_to_element(promo).click(promo).perform()
    #
    #
    # products = drive.find_element(By.CLASS_NAME, 'list')
    # posts = products.find_elements(By.TAG_NAME, 'rz-product-tile')
    # post_5 = posts[4].find_element(By.TAG_NAME, 'article').find_element(By.TAG_NAME, 'a')
    # href_5 = post_5.get_attribute('href')
    # drive.get(f'{href_5}')
    # time.sleep(2)
    #
    # for _ in range(10):
    #     drive.send_keys(Keys.ARROW_DOWN)
    #     time.sleep(0.3)
    #
    # time.sleep(5)
    #
    # for _ in range(10):
    #     drive.send_keys(Keys.ARROW_UP)
    #     time.sleep(0.3)
    #
    # main_page = drive.find_element(By.CSS_SELECTOR, 'img[alt="RozetkaLogo"]')
    # ActionChains(drive).move_to_element(main_page).click(main_page).perform()
    # time.sleep(3)
    #
    # search_elem = drive.find_element(By.CSS_SELECTOR, 'input[data-testid="search-suggest-input"]')
    # search_elem.clear()
    # search_elem.send_keys(req)
    # search_elem.send_keys(Keys.ENTER)
    # time.sleep(8)


def web_process(url, req, filt_by_price=False, sorting=False):
    """
        Function opens your browser and fetch url based on your preferences.

        params:
            url: str. URL of OLX resource
            req: str. Name of product which will be searched
            filt_by_price: bool, optional. If True then price range choice opportunity will be provided. Default = False.
            sorting: bool, optional. If True then sorting options will be provided (by New, by Old, by Popularity). Default = False.
        :return: list[str]. List of urls that parser function had fetched.
    """

    # Open browser
    drive = get_drive()
    drive.get(url)
    sleep(3)

    try:
        cookies = drive.find_element(By.CSS_SELECTOR, 'button[data-testid="dismiss-cookies-banner"]')
        cookies.click()
    except NoSuchElementException:
        pass

    # Pass into search field searching query
    search_element = drive.find_element(By.ID, 'search')
    search_element.send_keys(req)
    search_element.send_keys(Keys.ENTER)
    sleep(2)

    if filt_by_price:
        olx_filtration(drive)

    if sorting:
        olx_sorting(drive)

    title = drive.find_elements(By.CSS_SELECTOR, 'h4[class="css-hzlye5"]')
    links = []
    for t in title:
        if all(map(lambda x: x.lower() in t.text.lower(), req.split())):
            parent = t.find_element(By.XPATH, './..')
            a_tag = parent.get_attribute('href')
            links.append(a_tag)

    drive.close()
    return links


def get_info(url):
    """
        Function goes to the url and collect all necessary information.
        params:
            url: str. URL of OLX resource.
        :return: list[str]. List of strings that represents collected information.
    """

    info = [url]
    drive = webdriver.Chrome()
    try:
        drive.get(url)
    except Exception:
        pass
    else:
        try:
            error = drive.find_element(By.TAG_NAME, 'h1').text
        except NoSuchElementException:
            error = None
        else:
            while error == '403 ERROR':
                drive.refresh()
                sleep(1)
                try:
                    error = drive.find_element(By.TAG_NAME, 'h1').text
                except NoSuchElementException:
                    error = None

        if not error:
            try:
                username = drive.find_element(By.CSS_SELECTOR, 'h4[data-testid="user-profile-user-name"]').text
            except NoSuchElementException:
                username = '-' * 10
            info.append(username)

            try:
                userlink = drive.find_element(By.CSS_SELECTOR, 'a[data-testid="user-profile-link"]' ).get_attribute('href')
            except NoSuchElementException:
                userlink = '-' * 10
            info.append(userlink)

            try:
                post_id = int(drive.find_element(By.CSS_SELECTOR, 'span[class="css-ooacec"]').text.split()[1])
            except NoSuchElementException:
                post_id = int('1' * 8)
            info.append(post_id)

            try:
                product_title = drive.find_element(By.CSS_SELECTOR, 'h4[class="css-1au435n"]')
            except NoSuchElementException:
                product_title = 'Empty'
            info.append(product_title.text)

            try:
                product_price = drive.find_element(By.CSS_SELECTOR, 'h3[class="css-yauxmy"]')
                price = ''.join(x for x in product_price.text if x.isnumeric())
                if price:
                    price = float(price)
                else:
                    price = 0.00
            except NoSuchElementException:
                price = 0.00
            info.append(price)

            try:
                post_date = drive.find_element(By.CSS_SELECTOR, 'span[data-testid="ad-posted-at"]')
                converted_date = translate_date(post_date.text)
            except NoSuchElementException:
                converted_date = date.today()
            info.append(converted_date)
    finally:
        drive.close()

    return info


async def add_info(info, db_conn):
    """
        Coroutine function for adding info to database.

        params:
            info: list[str]. List of collected information.
            **kwargs: Keyword arguments to connect to your MySQL DB.
        :return: DB connection
    """

    cursor = db_conn.cursor()

    if len(info) < 2:
        return db_conn
    else:
        cursor.execute('''SELECT * FROM articles WHERE PostLink = %s''', (info[0],))
        data = cursor.fetchone()
        if not data:
            try:
                cursor.execute(
                    '''
                    INSERT INTO electronic_products (PostLink, UserName, UserLink, PostID, Title, ProductPrice, PostDate)
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                    ''', info)
                db_conn.commit()
            except mysql.connector.Error:
                db_conn.rollback()
        return db_conn


async def main():
    """
        Main process coroutine.
    :return: None
    """
    host = input('Enter host: ')
    user = input('Enter username: ')
    password = input('Enter password: ')
    db = input('Enter database name: ')

    conn = create_table(host=host, user=user, password=password, db=db)

    req = input('Enter preferred product name: ')
    filtr = input('Would you like to filter turn on? (Y/N): ')
    sorting_by = input('Would you like to sort by? (Y/N): ')

    if filtr == 'Y':
        filtr = True
    else:
        filtr = False

    if sorting_by == 'Y':
        sorting_by = True
    else:
        sorting_by = False

    links = web_process('https://www.olx.ua/uk/', req, filt_by_price=filtr, sorting=sorting_by)
    info_list = [get_info(link) for link in links]

    for i in range(len(info_list)):
        task = asyncio.create_task(add_info(info_list[i], conn))
        db = await task
        if i == len(info_list) - 1:
            db.close()


asyncio.run(main())




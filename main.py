import datetime
import time
import model
import dotenv
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementNotInteractableException,
    StaleElementReferenceException,
)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

dotenv.load_dotenv()

options = webdriver.FirefoxOptions()
options.add_argument("--headless")

driver = webdriver.Firefox(options=options)

url = os.getenv("URL")
driver.get(url)

href_list = []


def scrape_book(url: str) -> model.book:
    driver.get(url)

    main_content = driver.find_element(By.CLASS_NAME, "BookPage__mainContent")
    title = (
        main_content.find_element(By.CLASS_NAME, "BookPageTitleSection__title")
        .find_element(By.TAG_NAME, "h1")
        .text
    )
    author = main_content.find_element(
        By.CLASS_NAME, "BookPageMetadataSection__contributor"
    ).text

    rating = float(
        main_content.find_element(By.CLASS_NAME, "RatingStatistics__rating").text
    )
    rating_meta = main_content.find_element(
        By.CLASS_NAME, "RatingStatistics__meta"
    ).find_elements(By.TAG_NAME, "span")

    rating_count = int(rating_meta[0].text.split()[0].replace(",", ""))
    review_count = int(rating_meta[1].text.split()[0].replace(",", ""))

    description = (
        main_content.find_element(By.CLASS_NAME, "BookPageMetadataSection__description")
        .find_element(By.CLASS_NAME, "Formatted")
        .text
    )

    genres = main_content.find_element(
        By.CLASS_NAME, "BookPageMetadataSection__genres"
    ).text.split("\n")[1:-1]

    details = main_content.find_element(By.CLASS_NAME, "BookDetails").text.split()
    publish_date_index = details.index("published")

    pages = int(details[0])
    release_date = datetime.datetime.strptime(
        f"{details[publish_date_index+1]} {details[publish_date_index+2]} {details[publish_date_index+3]}",
        "%B %d, %Y",
    )

    interest_element = []

    while len(interest_element) != 2:
        interest_element = main_content.find_elements(
            By.CLASS_NAME, "SocialSignalsSection__caption"
        )
        time.sleep(3)

    currently_reading = int(
        interest_element[0]
        .text.split()[0]
        .replace(",", "")
        .replace(".", "")
        .replace("k", "000")
    )
    want_read = int(
        interest_element[1]
        .text.split()[0]
        .replace(",", "")
        .replace(".", "")
        .replace("k", "000")
    )

    return model.book(
        title=title,
        author=author,
        url=url,
        rating=rating,
        rating_count=rating_count,
        review_count=review_count,
        description=description,
        genres=genres,
        pages=pages,
        release_date=release_date.date(),
        currently_reading=currently_reading,
        want_to_read=want_read,
    )


def scrape_url():
    books = driver.find_elements(By.CLASS_NAME, "BookListItem")
    print("Books Count =", len(books))

    for book in books:
        href = (
            book.find_element(By.TAG_NAME, "h3")
            .find_element(By.TAG_NAME, "a")
            .get_attribute("href")
        )
        href_list.append(href)


def load_all():
    done = False
    while 1:
        try:
            load_more = driver.find_element(
                By.CLASS_NAME, "PopularByDatePage__paginationSelector"
            ).find_element(By.TAG_NAME, "button")

            if load_more.text == "loading more books":
                continue

            driver.execute_script("arguments[0].click();", load_more)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            if not done:
                try:
                    dialog = driver.find_element(By.CLASS_NAME, "Overlay__window")
                    close_dialog = dialog.find_element(By.TAG_NAME, "button")
                    close_dialog.click()
                    done = True
                except NoSuchElementException:
                    pass
                except ElementNotInteractableException:
                    pass

        except StaleElementReferenceException:
            continue

        except NoSuchElementException:
            print("Load More Button Not Found\nFinished")
            return

        except ElementNotInteractableException:
            print("Load More Button Not Interactable\nFinished")
            return


load_all()
scrape_url()

username = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASS")
host = os.getenv("MYSQL_HOST")
database = os.getenv("MYSQL_DB")

connection_string = f"mysql+pymysql://{username}:{password}@{host}/{database}"
print(connection_string)

engine = create_engine(connection_string)

Session = sessionmaker(bind=engine)
session = Session()

try:
    model.Base.metadata.create_all(engine)
except Exception as e:
    print("Error:", e)
    exit(1)

for href in href_list:
    try:
        new_book = scrape_book(href)
        session.add(new_book)
        session.commit()
        print("Added new book", new_book)
    except Exception as e:
        session.rollback()
        print("Error connecting to the database:", e)

session.close()
driver.quit()

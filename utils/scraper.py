from fastapi import HTTPException
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from loguru import logger


facebook_zona_url = "https://www.facebook.com/zonaetterem/"
facebook_last_img_xpath = '//*[@id=":rb:"]/div[1]/a'
facebook_quality_image_xpath = '//*[@id="scrollview"]/div/div/div/div[1]/div[1]/div/div[1]/div/div[1]/div/div[2]/div/div/div/img'
facebook_quality_image_xpath_css = ".x85a59c.x193iq5w.x4fas0m.x19kjcj4"


def get_element(xpath, driver, by=By.XPATH):
    logger.debug(f"getting element ➡️: {xpath}")
    element = None
    try:
        element = WebDriverWait(driver, 10).until(
            lambda x: x.find_element(
                by,
                xpath,
            )
        )
    except WebDriverException as e:
        logger.error(e)
        driver.quit()
        raise HTTPException(status_code=500, detail="Could not get element 🤬")
    return element


def create_driver():
    logger.debug("create_driver 🌍")
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("start-maximized")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")

    return webdriver.Chrome(options=options)


def get_this_weeks_zona_image_url():
    url = ""
    logger.debug("getting this weeks zona image url")
    driver = create_driver()

    try:
        driver.get(facebook_zona_url)
        last_img = get_element(facebook_last_img_xpath, driver)
        url_to_quality_image = last_img.get_attribute("href")
        if "&__cft__" in url_to_quality_image:
            logger.debug("junk found, removing it 🤮")
            url_to_quality_image = url_to_quality_image.split("&__cft__")[0]
        logger.debug(f"last_img: {url_to_quality_image}")

        driver.get(url_to_quality_image)

        quality_image = get_element(
            facebook_quality_image_xpath_css, driver, By.CSS_SELECTOR
        )
        # thats necessary because the image is lazy loaded or something 😢
        quality_image = get_element(
            facebook_quality_image_xpath_css, driver, By.CSS_SELECTOR
        )

        html_content = driver.page_source
        # logger.debug(f"html_content: {html_content}")

        logger.debug(f"quality_image: {quality_image.get_attribute('src')}")
        url = quality_image.get_attribute("src")
        driver.quit()

        return url
    except Exception as e:
        logger.error(e)
        driver.quit()
        raise HTTPException(status_code=500, detail="Could not get image url 🤬")

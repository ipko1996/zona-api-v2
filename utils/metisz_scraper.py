from loguru import logger
from selenium.webdriver.common.by import By
from utils.scraper import get_element, create_driver
import re


metisz_url = "https://www.metiszvendeglo.hu/napi-menu/"
week_ids = ["htf", "kedd", "szerda", "cstrtk", "pntek"]
not_shorted = ["HETFO", "KEDD", "SZERDA", "CSUTORTOK", "PENTEK"]
b_menu_id = "b-men"
week_from_to = '//*[@id="post-76"]/div/div[1]/div/div[4]/h1'
price_and_info = '//*[@id="post-76"]/div/div[1]/div/p'


def get_metisz_menu():
    meal_list = {
        "HETFO": [],
        "KEDD": [],
        "SZERDA": [],
        "CSUTORTOK": [],
        "PENTEK": [],
    }

    logger.debug("getting metisz menu")
    driver = create_driver()

    driver.get(metisz_url)
    price_text = get_element(price_and_info, driver)
    pattern = r"\b\d{4}\b"
    price = re.findall(pattern, price_text.text)[0]
    logger.debug(f"price: {price}")

    _b_menu = get_element(b_menu_id, driver, By.ID)
    parent = _b_menu.find_element(By.XPATH, "../..")
    b_menu = parent.find_element(By.TAG_NAME, "h3")

    for index, day in enumerate(week_ids):
        # not_shorted[index]
        day_id = day
        day = get_element(day_id, driver, By.ID)
        parent = day.find_element(By.XPATH, "../..")
        menu = parent.find_elements(By.TAG_NAME, "h3")
        tmp = ";".join([m.text[2:] for m in menu])
        meal_list[not_shorted[index]].append({"food": tmp, "price": price})
        # also add b menu for every day
        meal_list[not_shorted[index]].append({"food": b_menu.text[2:], "price": price})

    meal_list["error_while_parsing"] = False
    meal_list["url"] = metisz_url

    # pretty print meail_list
    # for day in meal_list:
    #     logger.debug(f"{day}: {meal_list[day]}")

    driver.quit()
    return meal_list

import gc
import re

import easyocr

from unidecode import unidecode
from loguru import logger


day_names = [
    "HETFO",
    "KEDD",
    "SZERDA",
    "CSUTORTOK",
    "PENTEK",
]
stop_word = "MENU"


def read_data(img):
    logger.debug("reading data...")
    reader = easyocr.Reader(["hu"], gpu=False, download_enabled=False)
    result = reader.readtext(
        image=img,
        detail=0,
        paragraph=False,
        width_ths=0.2,
    )
    return [unidecode(word) for word in result]


def serialize_price(price):
    # remove all none numeric characters
    str_price = re.sub(r"\D", "", price)
    return int(str_price)


def get_meal_list(result):
    logger.debug("creating meal list...")
    meal_list = {
        "HETFO": [],
        "KEDD": [],
        "SZERDA": [],
        "CSUTORTOK": [],
        "PENTEK": [],
    }

    logger.debug("lets not fall apart now 🤞")
    try:
        for day in day_names:
            # reset the iterator
            iterator = iter(result)
            # find the day in the result
            while True:
                temp = next(iterator)
                if day in temp:
                    # logger.debug(day)
                    food = ""
                    price = ""
                    while True:
                        temp = next(iterator)
                        if stop_word in temp:
                            food = ""
                            while True:
                                temp = next(iterator)
                                if any(char.isdigit() for char in temp):
                                    price = serialize_price(temp)
                                    meal_list[day].append(
                                        {"food": food, "price": price}
                                    )
                                    # logger.debug(f"MENU: {food} - {price}")
                                    food = ""
                                    break
                                else:
                                    food += temp + " "
                            break
                        if any(char.isdigit() for char in temp):
                            price = serialize_price(temp)
                            meal_list[day].append({"food": food, "price": price})
                            # logger.debug(f"{food} - {price}")
                            food = ""
                        else:
                            food += temp + " "
                    # logger.debug("\n")
                    break
    except StopIteration:
        logger.debug("Could not parse menu 🌶️👿🌶️")
        # raise HTTPException(status_code=500, detail="Could not parse menu")
        meal_list["error_while_parsing"] = True
        return meal_list
    finally:
        collected = gc.collect()
        logger.debug(f"Garbage collected:  {collected}")
        return meal_list

import datetime
import html
import re
import gc

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from prettytable import PrettyTable, ALL
from loguru import logger

from utils.db import get_db
from utils.img_to_text import get_meal_list, read_data
from utils.metisz_scraper import get_metisz_menu
from utils.scraper import get_this_weeks_zona_image_url
from utils.week_model import Menu, Restaurant

app = FastAPI(
    docs_url="/docs",
    redoc_url=None,
)


def get_current_year_and_week_string():
    logger.debug("getting current year and week 📅")
    current_date = datetime.datetime.now()
    current_year = current_date.isocalendar()[0]
    current_week = current_date.isocalendar()[1]
    return f"{current_year}{current_week}"


def get_previous_year_and_week_string():
    logger.debug("getting previous year and week ⬅️📅")
    current_date = datetime.datetime.now()
    previous_date = current_date - datetime.timedelta(weeks=1)

    # Check if the previous week is part of the first week of the year
    if previous_date.isocalendar()[1] == 53 and current_date.isocalendar()[1] == 1:
        previous_date -= datetime.timedelta(
            weeks=1
        )  # Adjust the date to consider it as part of the previous year

    previous_year = previous_date.isocalendar()[0]
    previous_week = previous_date.isocalendar()[1]
    return f"{previous_year}{previous_week}"


def is_same_jpg(url1, url2):
    # Use regex to find the JPG filenames in the URLs
    filename_match1 = re.search(r"/([^/]+\.(jpg|jpeg))", url1)
    filename_match2 = re.search(r"/([^/]+\.(jpg|jpeg))", url2)

    if filename_match1 and filename_match2:
        return filename_match1.group(1) == filename_match2.group(1)
    else:
        return False


def get_new_menu(current_week, db):
    logger.debug("getting new menu 🍽️")
    url = get_this_weeks_zona_image_url()

    # if url is emty raise error
    if not url:
        raise HTTPException(status_code=500, detail="Could not get image url 🤬")

    # if the url is same as the last one, the restaurant didn't update the menu yet
    logger.debug("checking if menu is updated 🤔")
    last_week = get_previous_year_and_week_string()
    last_week_menu = db["meals"].find_one({"week": last_week})
    if last_week_menu and is_same_jpg(url, last_week_menu["url"]):
        logger.debug("menu not updated yet")
        # todo: find out what to do if the menu is not updated
        raise HTTPException(
            status_code=404,
            detail="Menu not updated yet 🥵 🤤"
            + "\n"
            + "Meanwhile here is a good youtube video: https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        )

    zona_meal_list = get_meal_list(read_data(url))
    zona_temp = {
        # "week": current_week,
        "url": url,
        "error_while_parsing": zona_meal_list["error_while_parsing"]
        if "error_while_parsing" in zona_meal_list
        else False,
    }
    for day, meals in zona_meal_list.items():
        zona_temp[day] = meals

    metisz_meal_list = get_metisz_menu()
    metisz_temp = {
        # "week": current_week,
        "url": metisz_meal_list["url"],
        "error_while_parsing": metisz_meal_list["error_while_parsing"],
    }
    for day, meals in metisz_meal_list.items():
        metisz_temp[day] = meals

    temp = {
        "METISZ": metisz_temp,
        "ZONA": zona_temp,
        "week": current_week,
    }
    logger.debug(f"temp: {temp}")

    logger.debug("updloading new menu to db 📤")
    new_menu_id = db["meals"].insert_one(temp)
    # new_menu = db["meals"].find_one({"_id": new_menu_id.inserted_id})
    logger.debug("new menu uploaded to db, returning it 🤖")
    return temp


@app.get("/")
def read_root():
    return "alma"


@app.get("/weekly_meal", response_model=Restaurant)
def get_weekly_meal():
    current_week = get_current_year_and_week_string()
    db = get_db()
    logger.debug("trying to find menu in db 🕵️")
    weekly_meal = db["meals"].find_one({"week": current_week})

    try:
        if weekly_meal:
            logger.debug("found menu in db, returning it 🏎️")
            return weekly_meal
        else:
            logger.debug("menu not found in db, getting new one 🦥")
            new_menu = get_new_menu(current_week, db)
            return new_menu
    except Exception as e:
        logger.error(f"error happened {e}")
        raise HTTPException(
            status_code=500, detail="Something went wrong getting the menu ¯\_(ツ)_/¯"
        )
    finally:
        collected = gc.collect()
        logger.debug(f"Garbage collected:  {collected}")


@app.get("/weekly_meal/table", response_class=HTMLResponse)
def get_weekly_meal_table():
    weekly_meal = get_weekly_meal()
    logger.debug("creating html response")
    # check if we parsed the menu correctly
    print(weekly_meal["error_while_parsing"])
    if weekly_meal["error_while_parsing"]:
        logger.debug("could not parse menu earlier")
        return HTMLResponse(
            content=(
                "<h1>Could not parse the menu</h1>",
                "<h2>Must be a hell of an image...</h2>"
                "<a href='" + weekly_meal["url"] + "'>Link to image</a>",
            ),
            status_code=418,
        )

    # creating table
    logger.debug("creating the worlds most beautiful table 🤩")
    table = PrettyTable()

    url = weekly_meal["url"]
    url_text = "LINK TO IMAGE"
    week = weekly_meal["week"]

    weekly_meal.pop("url")
    weekly_meal.pop("week")
    weekly_meal.pop("_id")
    weekly_meal.pop("error_while_parsing")

    table.field_names = ["Meal", "Price"]

    for day, meals in weekly_meal.items():
        table.add_row(["<b>" + day + "</b>", ""])
        for meal in meals:
            # if the last meal of meals add devider
            if meal != meals[-1]:
                table.add_row([meal["food"], meal["price"]])
            else:
                table.add_row([meal["food"], meal["price"]], divider=True)

    table.add_row(["URL", "<a target='_blank' href=" + url + ">" + url_text + "</a>"])
    table.add_row(["WEEK_ID", week])

    table.align["Meal"] = "l"  # Left align city names
    table.align["Price"] = "r"  # Right align everything else

    table.format = True
    table.hrules = ALL
    table.vrules = ALL
    html_table_text = html.unescape(table.get_html_string())

    # oh my... 😊
    html_text = "<!-- ██████╗ ██╗   ██╗    ██╗██████╗ ██╗  ██╗ ██████╗  -->"
    html_text += "<!-- ██╔══██╗╚██╗ ██╔╝    ██║██╔══██╗██║ ██╔╝██╔═══██╗ -->"
    html_text += "<!-- ██████╔╝ ╚████╔╝     ██║██████╔╝█████╔╝ ██║   ██║ -->"
    html_text += "<!-- ██╔══██╗  ╚██╔╝      ██║██╔═══╝ ██╔═██╗ ██║   ██║ -->"
    html_text += "<!-- ██████╔╝   ██║       ██║██║     ██║  ██╗╚██████╔╝ -->"
    html_text += "<!-- ╚═════╝    ╚═╝       ╚═╝╚═╝     ╚═╝  ╚═╝ ╚═════╝  -->"
    html_text += "<!-- https://github.com/ipko1996 -->"

    html_text += html_table_text

    collected = gc.collect()
    logger.debug(f"Garbage collected:  {collected}")
    return HTMLResponse(content=html_text, status_code=200)

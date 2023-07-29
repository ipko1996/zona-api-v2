from pydantic import BaseModel, Field
from bson import ObjectId
from typing import List


class FoodItem(BaseModel):
    food: str
    price: int


class Menu(BaseModel):
    _id: ObjectId
    week: str = Field(alias="week")
    url: str
    HETFO: List[FoodItem]
    KEDD: List[FoodItem]
    SZERDA: List[FoodItem]
    CSUTORTOK: List[FoodItem]
    PENTEK: List[FoodItem]
    error_while_parsing: bool = False

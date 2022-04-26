from datetime import date

from pydantic import BaseModel


class RefuseCollection(BaseModel):
    collection_day: str
    next_rubbish: date
    next_recycling: date
    next_food_waste: date | None = None

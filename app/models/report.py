from pydantic import BaseModel

class Report(BaseModel):
    menu: str
    waste_ratio: float
    suggestion: str

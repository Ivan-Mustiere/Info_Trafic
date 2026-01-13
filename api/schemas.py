from pydantic import BaseModel

class PredictionInput(BaseModel):
    age: int
    tenure: int
    monthly_fee: float
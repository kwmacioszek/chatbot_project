from pydantic import BaseModel, Field

class AskRequest(BaseModel):
   question: str = Field(min_length=1, examples=["Ile kosztuje nadbagaż?"])

class AskResponse(BaseModel):
    answer: str = Field(examples=["Nadbagaż kosztuje 100 PLN."])
    
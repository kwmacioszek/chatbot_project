from pydantic import BaseModel, Field

class AskRequest(BaseModel):
   question: str = Field(min_length=1, examples=["Ile kosztuje nadbagaż?"])

class AskResponse(BaseModel):
    answer: str = Field(examples=["Nadbagaż kosztuje 100 PLN."])

class ChatRequest(BaseModel):
      question: str = Field(min_length=1, examples=["Ile kosztuje nadbagaż?"])
      session_id: str | None = Field(default=None, examples=["123e4567-e89b-12d3-a456-426614174000"])

class ChatResponse(BaseModel):
      answer: str = Field(examples=["Nadbagaż kosztuje 100 PLN."])
      session_id: str = Field(examples=["123e4567-e89b-12d3-a456-426614174000"])
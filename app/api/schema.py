# this file contains only for pydantic check

from pydantic import BaseModel, Field

class AskRequest(BaseModel):
    question:str = Field(
        ...,
        min_length=1,
        description="Question for RAG"
    )


# ---------------------------------------
class Source(BaseModel):
    chunk:str
    score:float

class AskResponse(BaseModel):
    request_id = str
    question: str
    answer: str
    source: list[Source]
    latency: float
    retrieval_latency:float
    generation_latency:float

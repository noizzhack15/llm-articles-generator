from pydantic import BaseModel, Field


class Article(BaseModel):
    reason: str = Field(description="Your reasoning for why this search is important to the query.")
    article_title: str
    article_body: str
    article_subject: str

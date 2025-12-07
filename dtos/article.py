from typing import Optional

from pydantic import BaseModel, Field


class Article(BaseModel):
    """
    Data Transfer Object for a generated article.
    """
    article_id: Optional[str] = Field(description="The article ID", default=None)
    title: str = Field(description="The professional title of the article.")
    summary: str = Field(description="A brief, 1-2 sentence summary of the article content.")
    article_body: str = Field(description="The complete, polished body of the article.")
    author: Optional[str] = Field(description="The author of the article.", default=None)
    destination: Optional[str] = Field(description="The destination person of the article.", default=None)

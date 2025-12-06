from pydantic import BaseModel, Field


class Article(BaseModel):
    """
    Data Transfer Object for a generated article.
    """
    title: str = Field(description="The professional title of the article.")
    summary: str = Field(description="A brief, 1-2 sentence summary of the article content.")
    article_body: str = Field(description="The complete, polished body of the article.")
    article_field: str = Field(description="the field of the article.")
    article_subdomain: str = Field(description="the subdomain of the article.")
    places: list[str] = Field(
        description="a list of places of the world this article applies to. This can be countries, cities, etc.")

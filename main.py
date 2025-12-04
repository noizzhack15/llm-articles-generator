import asyncio

from agents import Agent, Runner
from dotenv import load_dotenv
from openai import OpenAI

from dtos.article import Article

load_dotenv()

client = OpenAI()


def simple_text_generator():
    response = client.responses.create(
        model="gpt-5-nano",
        input="Write a one-sentence bedtime story about a unicorn."
    )

    return response.output_text


async def simple_text_generator_agent():
    agent = Agent(
        name="articles generator agent",
        instructions="""
אתה כתב חדשות מקצועי שעובד במערכת העיתון המוביל במדינת ישראל. 
תחום הסיקור שלך הינו ספורט. אתה כותב מאמרים בנושא זה. השתמש בשפה קולחת ותקנית. כתוב מאמר מקצועי ומעניין.
        """,
        output_type=Article,
        model="gpt-4o-mini"
    )

    result = await Runner.run(agent, "כתוב מאמר בנושא כדורגל. אורך המאמר צריך להיות לא יותר מ 200 מילים.")
    print(result.final_output.model_dump())


if __name__ == '__main__':
    asyncio.run(simple_text_generator_agent())

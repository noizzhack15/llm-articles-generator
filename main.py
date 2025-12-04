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
        instructions="you are a serious journalist and writer. you write very sad articles no matter what the subject is.",
        output_type=Article,
        model="gpt-4o-mini"
    )

    result = await Runner.run(agent, "Write a one-sentence article story about a unicorn.")
    print(result.final_output.model_dump())


if __name__ == '__main__':
    asyncio.run(simple_text_generator_agent())

import asyncio
import datetime
import os
import uuid

from agents import Agent, Runner, function_tool
from aio_pika import connect_robust, Message, DeliveryMode
from dotenv import load_dotenv
from faker import Faker

from dtos.article import Article

load_dotenv()
faker = Faker()
exchange = None


async def init_rabbitmq():
    global exchange

    if exchange is None:
        connection = await connect_robust(os.environ["RABBITMQ_URL"])
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            "breaking_ex",
            type="topic",
            durable=True)


@function_tool
async def send_article_to_queue(article: Article):
    """
    send an article object to a queue
    """
    article.article_id = str(uuid.uuid4())
    article.source = faker.name()
    article.publisher = faker.name()
    article.publication_date = datetime.datetime.now()
    article.recipients = []
    article.recipients.append(article.source)

    await init_rabbitmq()
    # The framework internally calls this tool if the agent successfully outputs the Article object
    print("\n--- Tool Execution: send_article_to_queue ---")
    print(f"Article:\n {article.model_dump()}")
    print("Sending article object to queue successful.")
    print("------------------------------------------\n")

    message = Message(
        body=article.model_dump_json().encode(),
        delivery_mode=DeliveryMode.PERSISTENT,
        content_type='application/json'
    )

    await exchange.publish(
        message,
        routing_key="test"
    )

    return "Article successfully sent to the queue."


async def run_simple_text_generator_agent():
    articles_queue_sender_agent = Agent(
        name="articles queue sender agent",
        instructions="""
             articles queue sender agent. **You have received an Article object**.
             Your only task is to use the `send_article_to_queue` tool to send this article object to a queue.
             You MUST use the `send_article_to_queue` tool.
             """,
        model="gpt-4.1-mini",
        handoff_description="send article object to a queue",
        tools=[send_article_to_queue]
    )

    with open(
            "c:/code_projects/breaking-bed/llm-articles-generator/prompts/eng/system_prompt.txt", 'r',
            encoding='utf-8') as file:
        articles_generator_agent_prompt = file.read()

    articles_generator_agent = Agent(
        name="articles generator agent",
        instructions=articles_generator_agent_prompt,
        output_type=Article,
        model="gpt-4.1-mini",
        handoffs=[articles_queue_sender_agent]
    )

    result = await Runner.run(
        articles_generator_agent,
        "write a short news article about soccer - no longer than 50 words. Be as specific as possible. Include places, people and events."
    )

    print(result)


if __name__ == '__main__':
    asyncio.run(run_simple_text_generator_agent())

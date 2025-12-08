import asyncio
import datetime
import os
import uuid
import random
import glob

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
    optional_recipients = ['הומר','מארג\'','בארט','ליסא מארי,', 'מגי','סנובול 1', ' סנובול 2']
    
    # 50% empty, 25% one recipient, 25% two recipients
    rand = random.random()
    if rand < 0.5:
        article.recipients = []
    elif rand < 0.75:
        article.recipients = [random.choice(optional_recipients)]
    else:
        article.recipients = random.sample(optional_recipients, 2)

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
        routing_key="rfeed"
    )

    return "Article successfully sent to the queue."


async def run_simple_text_generator_agent():
    # Define issues array with category mapping
    issues = [
        {"issue": "Foreign Policy", "category": "political"},
        {"issue": "Internal security", "category": "political"},
        {"issue": "Trade agreements", "category": "political"},
        {"issue": "tennis", "category": "sport"},
        {"issue": "soccer", "category": "sport"},
        {"issue": "Artificial intelligence", "category": "technology"},
        {"issue": "cellular devices", "category": "technology"}
    ]
    
    # Select a random issue
    selected_issue = random.choice(issues)
    issue_topic = selected_issue["issue"]
    issue_category = selected_issue["category"]
    
    print(f"Selected issue: {issue_topic} (Category: {issue_category})")
    
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

    # Load the matching prompt file based on the issue category
    prompt_file = f"prompts/eng/system_prompt_{issue_category}.txt"
    try:
        with open(prompt_file, 'r', encoding='utf-8') as file:
            articles_generator_agent_prompt = file.read()
        print(f"Using prompt file: {prompt_file}")
    except FileNotFoundError:
        print(f"Prompt file not found: {prompt_file}, using default")
        articles_generator_agent_prompt = "You are a news article generator."

    articles_generator_agent = Agent(
        name="articles generator agent",
        instructions=articles_generator_agent_prompt,
        output_type=Article,
        model="gpt-4.1-mini",
        handoffs=[articles_queue_sender_agent]
    )

    try:        
        result = await Runner.run(
            articles_generator_agent,
            f"generate a news article about {issue_topic} (≤100 words) and output it as an Article object (article_id, title, summary, article_body, author, destination). Be as specific as possible. Include places, people and events."
        )
        print(f"Final Result:\n{result}")
    except Exception as e:
        print(f"Error running article generator: {e}")


if __name__ == '__main__':
    async def main():
        for i in range(10):
            print(f"\n{'='*50}")
            print(f"Running iteration {i+1}/10")
            print(f"{'='*50}\n")
            await run_simple_text_generator_agent()
    
    asyncio.run(main())

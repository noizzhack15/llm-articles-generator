import asyncio

from agents import Agent, Runner, function_tool
from aio_pika import connect_robust, Message, DeliveryMode
from dotenv import load_dotenv

from dtos.article import Article

load_dotenv()

rabbitmq_data = {

}

exchange = None


async def init_rabbitmq():
    global exchange

    if exchange is None:
        connection = await connect_robust("amqp://guest:guest@localhost/breaking_bed")
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            "breaking_bed",
            type="topic",
            durable=True)


@function_tool
async def send_article_to_queue(article: Article):
    """
    send an article object to a queue
    """
    await init_rabbitmq()
    # The framework internally calls this tool if the agent successfully outputs the Article object
    print("\n--- Tool Execution: send_article_to_queue ---")
    print(f"Article Title: {article.title}")
    print(f"Article Summary: {article.summary}")
    print(f"Article Content (First 50 chars): {article.final_output[:50]}...")
    print("Sending article object to queue successful.")
    print("------------------------------------------\n")

    message = Message(
        body=article.model_dump_json().encode(),
        delivery_mode=DeliveryMode.PERSISTENT,  # Make the message durable
        content_type='application/json'  # Inform consumers about content type
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
         articles queue sender agent. you receive an article object and send it to a destination queue.
         use send_article_to_queue to send an article object to a queue.
         you must use that tool
         """,
        model="gpt-4o-mini",
        handoff_description="send article object to a queue",
        tools=[send_article_to_queue]
    )

    articles_generator_agent = Agent(
        name="articles generator agent",
        instructions="""
you are a professional journalist working for the leading daily news paper in the state of Israel. you cover the field of sports. you only write articles in that subject. 
Follow these steps carefully:
1. write articles in English only.
2. write articles using correct grammar.
3. the article you write must be interesting and professional.
4. Handoff for Sending: pass the generated article object to "articles queue sender agent". this agent will take care of sending the generated article to a destination queue.

Crucial Rules:
- You must hand off exactly ONE Article object (with fields: title, summary, final_output) to the "articles queue sender agent" 
""",
        output_type=Article,
        model="gpt-4o-mini",
        handoffs=[articles_queue_sender_agent]
    )

    result = await Runner.run(
        articles_generator_agent,
        "write a short article about soccer - no longer than 20 words"
    )


if __name__ == '__main__':
    asyncio.run(run_simple_text_generator_agent())

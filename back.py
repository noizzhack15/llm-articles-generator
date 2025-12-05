import asyncio

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
# We use 'langchain_openai' for the ChatOpenAI class, as it's the current standard
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# --- LOCALAI CONFIGURATION ---
# Base URL must include /v1 for LangChain's ChatOpenAI to correctly form the final API path
LOCALAI_BASE_URL = "http://localhost:8080/v1"

# Initialize the LangChain ChatOpenAI object to point to LocalAI.
# NOTE: Using ChatOpenAI from 'langchain_openai' as it is the current, fully supported package.
llm = ChatOpenAI(
    model="llama3.1",
    openai_api_base=LOCALAI_BASE_URL,
    openai_api_key="no-key",  # Dummy key
    temperature=0.0,
    max_retries=1
)


# -----------------------------

# --- Data Model: Article ---
class Article(BaseModel):
    """Data Transfer Object for a generated article."""
    title: str = Field(description="The professional title of the article.")
    summary: str = Field(description="A brief, 1-2 sentence summary of the article content.")
    final_output: str = Field(description="The complete, polished body of the article.")


load_dotenv()


# --- Post-processing Function (Replaces Agent/Tool Call) ---
def send_article_to_queue(article: Article) -> str:
    """
    Sends the fully generated Article object to a destination queue.
    This is called manually after the LLM successfully generates the Pydantic object.
    """
    print("\n--- Tool Execution: send_article_to_queue ---")
    print(f"Article Title: {article.title}")
    print(f"Article Summary: {article.summary}")
    print(f"Article Content (First 50 chars): {article.final_output[:50]}...")
    print("Sending article object to queue successful.")
    print("------------------------------------------\n")
    return "Article successfully sent to the queue."


# --- Prompt Definition ---
SYSTEM_PROMPT = """
You are a professional journalist working for the leading daily news paper in the state of Israel. 
You cover the field of sports and must ONLY write articles in that subject. 
Your sole task is to generate a professional Article based on the user's request.

Follow these steps carefully:
1. Write articles in English only, using correct grammar.
2. The article you write must be interesting and professional.
3. You MUST respond ONLY with a valid JSON object that strictly adheres to the provided schema for the Article object.
"""

# The LangChain Prompt
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", "{user_input}"),
    ]
)


async def simple_text_generator_agent_lc():
    # 3. --- Create the Runnable Chain using with_structured_output ---
    # This automatically prompts the model for JSON output and parses it into the Article schema.
    # We use method="json_mode" for non-native function calling models.
    llm_with_output_schema = llm.with_structured_output(schema=Article, method="json_mode")

    # The chain: Prompt -> LLM with Structured Output
    agent_chain = prompt | llm_with_output_schema

    user_request = "write a professional article in English about football. the article must be no longer than 10 words."

    # 4. --- Execute the Chain ---
    try:
        # The result_dto is the Pydantic Article object itself upon successful generation
        print("Invoking LangChain agent chain...")
        result_dto = await agent_chain.ainvoke({"user_input": user_request})

        print("\n--- Final LangChain Result Object ---")
        print(f"Result Type: {type(result_dto)}")
        print("Final Output (Article DTO):")
        print(result_dto.model_dump())

        # 5. --- Call the final function/tool manually with the generated object ---
        send_article_to_queue(result_dto)

    except Exception as e:
        print(f"\n--- LangChain Execution Failed ---")
        print(f"Error: {e}")
        print("\nEnsure LocalAI is running and the model name 'llama3.1' matches your LocalAI configuration.")


if __name__ == '__main__':
    asyncio.run(simple_text_generator_agent_lc())

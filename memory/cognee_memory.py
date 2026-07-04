import cognee
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

USE_COGNEE_CLOUD = os.getenv("USE_COGNEE_CLOUD", "false").lower() == "true"

COGNEE_SERVICE_URL = (
    os.getenv("COGNEE_SERVICE_URL")
    or os.getenv("COGNEE_API_BASE_URL")
)

COGNEE_API_KEY = os.getenv("COGNEE_API_KEY")

DATASET_NAME = "fixmind_debug_memory"


async def connect_cognee():
    """
    Connect FixMind to Cognee Cloud only if USE_COGNEE_CLOUD=true.
    """
    if not USE_COGNEE_CLOUD:
        return

    if not COGNEE_SERVICE_URL:
        raise ValueError(
            "COGNEE_SERVICE_URL or COGNEE_API_BASE_URL is missing in .env"
        )

    if not COGNEE_API_KEY:
        raise ValueError(
            "COGNEE_API_KEY is missing in .env"
        )

    await cognee.serve(
        url=COGNEE_SERVICE_URL,
        api_key=COGNEE_API_KEY
    )


async def disconnect_cognee():
    """
    Safely disconnect from Cognee Cloud.
    """
    if not USE_COGNEE_CLOUD:
        return

    try:
        await cognee.disconnect()
    except Exception:
        pass


async def add_memory_to_cognee(problem, solution):
    """
    Save a solved debugging issue into Cognee semantic memory.
    """
    await connect_cognee()

    try:
        memory_text = f"""
FixMind Embedded Systems Debug Memory

Problem:
{problem}

Solution:
{solution}

Tags:
embedded systems,
hardware debugging,
firmware,
UART,
SPI,
I2C,
ADC,
GPIO,
ESP32,
STM32,
Arduino
"""

        await cognee.remember(
            memory_text,
            dataset_name=DATASET_NAME
        )

        return True

    except Exception as e:
        print("Cognee Cloud save error:", e)
        return False

    finally:
        await disconnect_cognee()


async def search_cognee_memory(query):
    """
    Search Cognee semantic memory for similar previous debugging issues.
    """
    await connect_cognee()

    try:
        results = await cognee.recall(
            query_text=query,
            datasets=[DATASET_NAME]
        )

        if not results:
            return []

        return results

    except Exception as e:
        print("Cognee Cloud recall error:", e)
        return []

    finally:
        await disconnect_cognee()


def remember_with_cognee(problem, solution):
    """
    Streamlit-safe wrapper for saving memory to Cognee.
    """
    try:
        return asyncio.run(add_memory_to_cognee(problem, solution))
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(add_memory_to_cognee(problem, solution))
        loop.close()
        return result
    except Exception as e:
        print("Cognee wrapper save error:", e)
        return False


def recall_with_cognee(query):
    """
    Streamlit-safe wrapper for recalling memory from Cognee.
    """
    try:
        return asyncio.run(search_cognee_memory(query))
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(search_cognee_memory(query))
        loop.close()
        return result
    except Exception as e:
        print("Cognee wrapper recall error:", e)
        return []
    

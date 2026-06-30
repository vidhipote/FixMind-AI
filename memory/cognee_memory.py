import cognee
import asyncio


async def add_memory_to_cognee(problem, solution):
    memory_text = f"""
Debugging Problem:
{problem}

Solution:
{solution}
"""
    await cognee.add(memory_text)
    await cognee.cognify()


async def search_cognee_memory(query):
    results = await cognee.search(query)
    return results


async def delete_cognee_memory(query):
    await cognee.forget(query)


def remember_with_cognee(problem, solution):
    try:
        asyncio.run(add_memory_to_cognee(problem, solution))
        return True
    except Exception as e:
        print("Cognee save error:", e)
        return False


def recall_with_cognee(query):
    try:
        results = asyncio.run(search_cognee_memory(query))
        return results
    except Exception as e:
        print("Cognee recall error:", e)
        return []


def forget_from_cognee(query):
    try:
        asyncio.run(delete_cognee_memory(query))
        return True
    except Exception as e:
        print("Cognee forget error:", e)
        return False




#old code
# import cognee
# import asyncio

# async def add_memory_to_cognee(problem, solution):
#     memory_text = f"""
# Debugging Problem:
# {problem}

# Solution:
# {solution}
# """
#     await cognee.add(memory_text)
#     await cognee.cognify()

# async def search_cognee_memory(query):
#     results = await cognee.search(query)
#     return results

# def remember_with_cognee(problem, solution):
#     try:
#         asyncio.run(add_memory_to_cognee(problem, solution))
#         return True
#     except Exception as e:
#         print("Cognee save error:", e)
#         return False

# def recall_with_cognee(query):
#     try:
#         results = asyncio.run(search_cognee_memory(query))
#         return results
#     except Exception as e:
#         print("Cognee recall error:", e)
#         return []
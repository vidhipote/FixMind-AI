import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

from memory.memory_manager import (
    save_memory,
    load_memories,
    search_memory,
    delete_memory,
)

from memory.cognee_memory import remember_with_cognee, recall_with_cognee

load_dotenv()

USE_COGNEE = os.getenv("USE_COGNEE", "false").lower() == "true"

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")


def ask_gemini(problem):
    prompt = f"""
You are FixMind, a senior Embedded Systems debugging assistant.

User problem:
{problem}

Give a SHORT, practical debugging response.

Use exactly this format:

### Possible Causes
- Cause 1
- Cause 2
- Cause 3
- Cause 4

### Step-by-Step Checks
1. Check ...
2. Verify ...
3. Test ...
4. Confirm ...

### Most Likely Fix
Write the most likely fix in 2-3 lines.

### Prevention Tip
Write one practical prevention tip.

Rules:
- Keep the answer concise.
- Focus on STM32, ESP32, Arduino, UART, SPI, I2C, ADC, ESP32, sensors, embedded hardware.
"""
    response = model.generate_content(prompt)
    return response.text


def format_cognee_results(results):
    if not results:
        return ""

    invalid_phrases = [
        "does not contain any information",
        "does not contain information",
        "provided context does not",
        "no information about",
        "cannot answer",
        "not enough information",
        "no relevant information",
    ]

    text = str(results).strip()

    if any(phrase in text.lower() for phrase in invalid_phrases):
        return ""

    try:
        if isinstance(results, list):
            first = results[0]

            if isinstance(first, dict):
                search_result = first.get("search_result", "")

                if isinstance(search_result, list) and search_result:
                    result_text = str(search_result[0])
                    if any(phrase in result_text.lower() for phrase in invalid_phrases):
                        return ""
                    return result_text

                if isinstance(search_result, str):
                    if any(phrase in search_result.lower() for phrase in invalid_phrases):
                        return ""
                    return search_result

    except Exception:
        pass

    return text


st.set_page_config(page_title="FixMind", page_icon="🛠️", layout="wide")

st.sidebar.title("🛠️ FixMind")
page = st.sidebar.radio("Navigation", ["Home", "Memory History", "About"])

for key, default in {
    "problem": "",
    "answer": "",
    "memory_found": [],
    "selected_memory": None,
    "show_memory": False,
    "show_ai_answer": False,
    "saved": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


if page == "Home":
    st.title("🛠️ FixMind")
    st.subheader("Your Personal Engineering Memory")

    st.write("""
Describe your Embedded Systems problem below.

Examples:
- STM32 UART not transmitting
- ESP32 WiFi not connecting
- SPI communication failed
- I2C device not detected
""")

    problem_input = st.text_area(
        "Describe your debugging issue",
        height=150,
        value=st.session_state.problem
    )

    if st.button("Ask FixMind"):
        if problem_input.strip() == "":
            st.warning("Please enter your problem.")
        else:
            st.session_state.problem = problem_input
            st.session_state.answer = ""
            st.session_state.memory_found = []
            st.session_state.selected_memory = None
            st.session_state.show_memory = False
            st.session_state.show_ai_answer = False
            st.session_state.saved = False

            formatted_cognee = ""

            if USE_COGNEE:
                with st.spinner("Searching Cognee memory..."):
                    cognee_results = recall_with_cognee(problem_input)
                    formatted_cognee = format_cognee_results(cognee_results)

            if formatted_cognee:
                st.session_state.memory_found = [{
                    "problem": "Cognee Semantic Memory Match",
                    "date": "Retrieved from Cognee",
                    "solution": formatted_cognee
                }]
            else:
                st.session_state.memory_found = search_memory(problem_input)

            if not st.session_state.memory_found:
                st.session_state.show_ai_answer = True

    if st.session_state.memory_found and not st.session_state.show_ai_answer:
        memory = st.session_state.memory_found[0]
        st.info("🧠 Similar debugging session found.")

        st.markdown(f"**Previous Problem:** {memory['problem']}")
        st.write(f"**Saved:** {memory['date']}")

        col1, col2 = st.columns([1, 1])

        with col1:
            if st.button("👁 View Previous Fix"):
                st.session_state.selected_memory = memory
                st.session_state.show_memory = True
                st.session_state.show_ai_answer = False

        with col2:
            if st.button("✨ Generate New AI Solution"):
                st.session_state.selected_memory = None
                st.session_state.show_memory = False
                st.session_state.show_ai_answer = True
                st.session_state.answer = ""
                st.session_state.saved = False

    if st.session_state.show_memory and st.session_state.selected_memory:
        memory = st.session_state.selected_memory

        st.markdown("## Previous Fix")
        st.write(f"**Problem:** {memory['problem']}")
        st.write(f"**Date:** {memory['date']}")
        st.markdown(memory["solution"])

    if st.session_state.show_ai_answer:
        if st.session_state.answer == "":
            with st.spinner("FixMind is thinking..."):
                try:
                    st.session_state.answer = ask_gemini(st.session_state.problem)
                except Exception as e:
                    st.error("Gemini connection failed.")
                    st.code(str(e))

        if st.session_state.answer:
            st.success("FixMind Response")
            st.markdown(st.session_state.answer)

            st.divider()

            if not st.session_state.saved:
                if st.button("✅ Mark as Solved and Save Memory"):
                    json_saved = save_memory(
                        st.session_state.problem,
                        st.session_state.answer
                    )

                    cognee_saved = False

                    if USE_COGNEE:
                        with st.spinner("Saving to Cognee memory..."):
                            cognee_saved = remember_with_cognee(
                                st.session_state.problem,
                                st.session_state.answer
                            )

                    st.session_state.saved = True

                    if USE_COGNEE and cognee_saved:
                        st.success("Memory saved successfully in JSON + Cognee!")
                    elif not USE_COGNEE:
                        if json_saved:
                            st.success("Memory saved successfully in JSON. Cognee is disabled.")
                        else:
                            st.info("This memory already exists in JSON.")
                    else:
                        if json_saved:
                            st.warning("Saved in JSON. Cognee memory failed, but JSON backup is safe.")
                        else:
                            st.info("This memory already exists in JSON.")
            else:
                st.info("This solution is already saved.")


elif page == "Memory History":
    st.title("📚 Memory History")

    memories = load_memories()

    if not memories:
        st.info("No memories stored yet.")
    else:
        st.success(f"{len(memories)} debugging memories stored.")

        for index, memory in enumerate(memories):
            with st.expander(f"{index + 1}. {memory['problem']}"):
                st.write(f"**Date:** {memory['date']}")
                st.markdown(memory["solution"])

                if st.button("🗑 Delete Memory", key=f"delete_{index}"):
                    delete_memory(index)
                    st.success("Memory deleted successfully!")
                    st.rerun()


else:
    st.title("About FixMind")

    st.write("""
FixMind is an AI-powered debugging assistant for Embedded Systems engineers.

It remembers previous debugging sessions and recalls similar past fixes using JSON backup and Cognee semantic memory.

Developed for the WeMakeDevs Hackathon.
""")
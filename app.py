import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

from memory.memory_manager import save_memory, load_memories, search_memory

load_dotenv()

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
- Do not write long theory.
- Focus on STM32, ESP32, UART, SPI, I2C, ADC, sensors, embedded hardware.
- Avoid unnecessary code unless absolutely needed.
"""
    response = model.generate_content(prompt)
    return response.text


st.set_page_config(page_title="FixMind", page_icon="🛠️", layout="wide")

st.sidebar.title("🛠️ FixMind")
page = st.sidebar.radio("Navigation", ["Home", "Memory History", "About"])

if "problem" not in st.session_state:
    st.session_state.problem = ""

if "answer" not in st.session_state:
    st.session_state.answer = ""

if "memory_found" not in st.session_state:
    st.session_state.memory_found = []

if "show_ai_answer" not in st.session_state:
    st.session_state.show_ai_answer = False


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
            st.session_state.show_ai_answer = False
            st.session_state.memory_found = search_memory(problem_input)

    if st.session_state.memory_found and not st.session_state.show_ai_answer:
        st.info("🧠 Similar memory found from your previous debugging sessions.")

        memory = st.session_state.memory_found[0]

        st.markdown("## Previous Fix")
        st.write(f"**Problem:** {memory['problem']}")
        st.write(f"**Date:** {memory['date']}")
        st.markdown(memory["solution"])

        st.divider()

        if st.button("Generate New AI Solution"):
            st.session_state.show_ai_answer = True

    if (not st.session_state.memory_found and st.session_state.problem) or st.session_state.show_ai_answer:
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

            if st.button("✅ Mark as Solved and Save Memory"):
                save_memory(st.session_state.problem, st.session_state.answer)
                st.success("Memory saved successfully!")


elif page == "Memory History":
    st.title("📚 Memory History")

    memories = load_memories()

    if not memories:
        st.info("No memories stored yet.")
    else:
        st.success(f"{len(memories)} debugging memories stored.")

        for index, memory in enumerate(reversed(memories), start=1):
            with st.expander(f"{index}. {memory['problem']}"):
                st.write(f"**Date:** {memory['date']}")
                st.markdown(memory["solution"])


else:
    st.title("About FixMind")

    st.write("""
FixMind is an AI-powered debugging assistant for Embedded Systems engineers.

It remembers previous debugging sessions and recalls similar past fixes.

Developed for the WeMakeDevs Hackathon.
""")
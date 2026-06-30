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
- Focus on STM32, ESP32, Arduino, UART, SPI, I2C, ADC, sensors, embedded hardware.
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


st.set_page_config(
    page_title="FixMind",
    page_icon="🛠️",
    layout="wide"
)


st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #020617 0%, #0f172a 45%, #111827 100%);
    color: #e5e7eb;
}

/* Animated circuit background */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(56,189,248,0.07) 1px, transparent 1px),
        linear-gradient(90deg, rgba(56,189,248,0.07) 1px, transparent 1px);
    background-size: 42px 42px;
    animation: circuitMove 18s linear infinite;
    pointer-events: none;
    z-index: 0;
}

@keyframes circuitMove {
    from { background-position: 0 0; }
    to { background-position: 120px 120px; }
}

section[data-testid="stSidebar"] {
    background: #020617;
    border-right: 1px solid #1e293b;
}

section[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}

h1, h2, h3 {
    color: #38bdf8 !important;
    font-weight: 800 !important;
}

p, li, label {
    color: #d1d5db !important;
}

.hardware-card {
    background: linear-gradient(135deg, #0f172a, #111827);
    border: 1px solid #334155;
    border-radius: 22px;
    padding: 32px;
    margin-bottom: 26px;
    box-shadow: 0 0 28px rgba(56, 189, 248, 0.15);
    animation: softGlow 3s ease-in-out infinite alternate;
}

@keyframes softGlow {
    from {
        box-shadow: 0 0 18px rgba(56, 189, 248, 0.12);
    }
    to {
        box-shadow: 0 0 34px rgba(34, 197, 94, 0.24);
    }
}

.ai-chip {
    font-size: 62px;
    animation: floatChip 3s ease-in-out infinite;
    text-shadow: 0 0 22px rgba(56,189,248,0.7);
}

@keyframes floatChip {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-12px); }
    100% { transform: translateY(0px); }
}

.led {
    height: 12px;
    width: 12px;
    background-color: #22c55e;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 12px #22c55e;
    animation: blink 1.2s infinite;
    margin-right: 8px;
}

@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.25; }
}

.feature-badge {
    display: inline-block;
    background: #064e3b;
    color: #bbf7d0;
    padding: 8px 15px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 700;
    margin: 5px 6px 0 0;
}

.warning-badge {
    display: inline-block;
    background: #78350f;
    color: #fde68a;
    padding: 8px 15px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 700;
    margin: 5px 6px 0 0;
}

.memory-card {
    background: #0f172a;
    border-left: 5px solid #22c55e;
    border-radius: 18px;
    padding: 22px;
    margin: 20px 0;
    box-shadow: 0 0 18px rgba(34, 197, 94, 0.14);
}

.response-card {
    background: #020617;
    border: 1px solid #334155;
    border-radius: 18px;
    padding: 24px;
    margin-top: 18px;
    box-shadow: 0 0 18px rgba(56, 189, 248, 0.12);
}

.stat-card {
    background: #111827;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 0 15px rgba(56,189,248,0.08);
}

.stat-number {
    font-size: 32px;
    font-weight: 900;
    color: #22c55e;
}

.stat-label {
    font-size: 14px;
    color: #94a3b8;
}

.stTextArea textarea {
    background-color: #020617 !important;
    color: #e5e7eb !important;
    border: 1px solid #94a3b8 !important;
    border-radius: 14px !important;
}

.stButton button {
    background: linear-gradient(90deg, #0284c7, #22c55e);
    color: white !important;
    border: none;
    border-radius: 12px;
    padding: 0.65rem 1.1rem;
    font-weight: 700;
    transition: 0.25s ease;
    position: relative;
    overflow: hidden;
}

.stButton button:hover {
    background: linear-gradient(90deg, #0369a1, #16a34a);
    transform: scale(1.02);
    color: white !important;
    border: none;
}

.stButton button::after {
    content: "";
    position: absolute;
    top: 0;
    left: -80%;
    width: 50%;
    height: 100%;
    background: rgba(255,255,255,0.25);
    transform: skewX(-20deg);
    animation: shine 3s infinite;
}

@keyframes shine {
    0% { left: -80%; }
    50% { left: 130%; }
    100% { left: 130%; }
}

div[data-testid="stAlert"] {
    border-radius: 14px;
}

hr {
    border-color: #334155;
}

</style>
""", unsafe_allow_html=True)


st.sidebar.markdown("## 🛠️ FixMind")
st.sidebar.markdown("### Embedded AI Debugger")
page = st.sidebar.radio("Navigation", ["🏠 Home", "📚 Memory History", "ℹ️ About"])

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


if page == "🏠 Home":
    memories = load_memories()

    st.markdown("""
    <div class="hardware-card">
        <div style="display:flex; align-items:center; gap:25px;">
            <div class="ai-chip">⚙️</div>
            <div>
                <h1>🛠️ FixMind</h1>
                <h3>AI-Powered Embedded Systems Debugging Memory</h3>
                <p><span class="led"></span>System Online · Memory Active · Hardware Debug Mode</p>
                <span class="feature-badge">Gemini AI</span>
                <span class="feature-badge">Cognee Semantic Memory</span>
                <span class="feature-badge">JSON Backup</span>
                <span class="warning-badge">Embedded Systems</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{len(memories)}</div>
            <div class="stat-label">Stored Memories</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">AI</div>
            <div class="stat-label">Debugging Engine</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        cognee_status = "ON" if USE_COGNEE else "OFF"
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{cognee_status}</div>
            <div class="stat-label">Cognee Memory</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🔧 Describe Your Embedded Systems Problem")

    problem_input = st.text_area(
        "Examples: STM32 UART not transmitting, ESP32 WiFi not connecting, I2C device not detected",
        height=150,
        value=st.session_state.problem
    )

    if st.button("🚀 Ask FixMind"):
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

        st.markdown(f"""
        <div class="memory-card">
            <h3>🧠 Similar Engineering Memory Found</h3>
            <p><b>Stored Problem:</b> {memory['problem']}</p>
            <p><b>Saved:</b> {memory['date']}</p>
            <p>This previous debugging session may help with your current hardware issue.</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

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

        st.markdown('<div class="response-card">', unsafe_allow_html=True)
        st.markdown("## Previous Fix")
        st.write(f"**Problem:** {memory['problem']}")
        st.write(f"**Date:** {memory['date']}")
        st.markdown(memory["solution"])
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.show_ai_answer:
        if st.session_state.answer == "":
            with st.spinner("FixMind is analyzing your hardware issue..."):
                try:
                    st.session_state.answer = ask_gemini(st.session_state.problem)
                except Exception as e:
                    st.error("Gemini connection failed.")
                    st.code(str(e))

        if st.session_state.answer:
            st.success("✅ FixMind Response")

            st.markdown('<div class="response-card">', unsafe_allow_html=True)
            st.markdown(st.session_state.answer)
            st.markdown('</div>', unsafe_allow_html=True)

            st.divider()

            if not st.session_state.saved:
                if st.button("💾 Mark as Solved and Save Memory"):
                    json_saved = save_memory(
                        st.session_state.problem,
                        st.session_state.answer
                    )

                    cognee_saved = False

                    if USE_COGNEE:
                        with st.spinner("Saving to Cognee semantic memory..."):
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
                            st.warning("Saved in JSON. Cognee failed, but backup memory is safe.")
                        else:
                            st.info("This memory already exists in JSON.")
            else:
                st.info("This solution is already saved.")


elif page == "📚 Memory History":
    st.markdown("""
    <div class="hardware-card">
        <div style="display:flex; align-items:center; gap:25px;">
            <div class="ai-chip">🧠</div>
            <div>
                <h1>📚 Memory History</h1>
                <h3>Previously solved embedded debugging sessions</h3>
                <p><span class="led"></span>Local JSON memory active</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    memories = load_memories()

    if not memories:
        st.info("No memories stored yet.")
    else:
        st.success(f"{len(memories)} debugging memories stored.")

        for index, memory in enumerate(memories):
            with st.expander(f"🧠 {index + 1}. {memory['problem']}"):
                st.write(f"**Date:** {memory['date']}")
                st.markdown(memory["solution"])

                if st.button("🗑 Delete Memory", key=f"delete_{index}"):
                    delete_memory(index)
                    st.success("Memory deleted successfully!")
                    st.rerun()


else:
    st.markdown("""
    <div class="hardware-card">
        <div style="display:flex; align-items:center; gap:25px;">
            <div class="ai-chip">🔌</div>
            <div>
                <h1>ℹ️ About FixMind</h1>
                <h3>AI debugging memory for embedded systems engineers</h3>
                <p>
                FixMind helps engineers debug STM32, ESP32, Arduino, sensors,
                UART, SPI, I2C, ADC, and hardware communication problems.
                </p>
                <span class="feature-badge">Gemini</span>
                <span class="feature-badge">Cognee</span>
                <span class="feature-badge">Streamlit</span>
                <span class="feature-badge">GitHub Backup</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# #No.2 Working Code with UI
# import streamlit as st
# import google.generativeai as genai
# from dotenv import load_dotenv
# import os

# from memory.memory_manager import (
#     save_memory,
#     load_memories,
#     search_memory,
#     delete_memory,
# )

# from memory.cognee_memory import remember_with_cognee, recall_with_cognee

# load_dotenv()

# USE_COGNEE = os.getenv("USE_COGNEE", "false").lower() == "true"

# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# model = genai.GenerativeModel("gemini-2.5-flash")


# def ask_gemini(problem):
#     prompt = f"""
# You are FixMind, a senior Embedded Systems debugging assistant.

# User problem:
# {problem}

# Give a SHORT, practical debugging response.

# Use exactly this format:

# ### Possible Causes
# - Cause 1
# - Cause 2
# - Cause 3
# - Cause 4

# ### Step-by-Step Checks
# 1. Check ...
# 2. Verify ...
# 3. Test ...
# 4. Confirm ...

# ### Most Likely Fix
# Write the most likely fix in 2-3 lines.

# ### Prevention Tip
# Write one practical prevention tip.

# Rules:
# - Keep the answer concise.
# - Focus on STM32, ESP32, Arduino, UART, SPI, I2C, ADC, sensors, embedded hardware.
# """
#     response = model.generate_content(prompt)
#     return response.text


# def format_cognee_results(results):
#     if not results:
#         return ""

#     invalid_phrases = [
#         "does not contain any information",
#         "does not contain information",
#         "provided context does not",
#         "no information about",
#         "cannot answer",
#         "not enough information",
#         "no relevant information",
#     ]

#     text = str(results).strip()

#     if any(phrase in text.lower() for phrase in invalid_phrases):
#         return ""

#     try:
#         if isinstance(results, list):
#             first = results[0]

#             if isinstance(first, dict):
#                 search_result = first.get("search_result", "")

#                 if isinstance(search_result, list) and search_result:
#                     result_text = str(search_result[0])
#                     if any(phrase in result_text.lower() for phrase in invalid_phrases):
#                         return ""
#                     return result_text

#                 if isinstance(search_result, str):
#                     if any(phrase in search_result.lower() for phrase in invalid_phrases):
#                         return ""
#                     return search_result

#     except Exception:
#         pass

#     return text


# st.set_page_config(
#     page_title="FixMind",
#     page_icon="🛠️",
#     layout="wide"
# )


# st.markdown("""
# <style>
# .stApp {
#     background: linear-gradient(135deg, #020617 0%, #0f172a 45%, #111827 100%);
#     color: #e5e7eb;
# }

# section[data-testid="stSidebar"] {
#     background: #020617;
#     border-right: 1px solid #1e293b;
# }

# section[data-testid="stSidebar"] * {
#     color: #e5e7eb !important;
# }

# h1, h2, h3 {
#     color: #38bdf8 !important;
#     font-weight: 800 !important;
# }

# p, li, label {
#     color: #d1d5db !important;
# }

# .hardware-card {
#     background: linear-gradient(135deg, #0f172a, #111827);
#     border: 1px solid #334155;
#     border-radius: 20px;
#     padding: 28px;
#     margin-bottom: 24px;
#     box-shadow: 0 0 28px rgba(56, 189, 248, 0.15);
# }

# .feature-badge {
#     display: inline-block;
#     background: #064e3b;
#     color: #bbf7d0;
#     padding: 7px 14px;
#     border-radius: 999px;
#     font-size: 13px;
#     font-weight: 700;
#     margin: 5px 6px 0 0;
# }

# .warning-badge {
#     display: inline-block;
#     background: #78350f;
#     color: #fde68a;
#     padding: 7px 14px;
#     border-radius: 999px;
#     font-size: 13px;
#     font-weight: 700;
#     margin: 5px 6px 0 0;
# }

# .memory-card {
#     background: #0f172a;
#     border-left: 5px solid #22c55e;
#     border-radius: 18px;
#     padding: 20px;
#     margin: 18px 0;
#     box-shadow: 0 0 18px rgba(34, 197, 94, 0.12);
# }

# .response-card {
#     background: #020617;
#     border: 1px solid #334155;
#     border-radius: 18px;
#     padding: 22px;
#     margin-top: 18px;
#     box-shadow: 0 0 18px rgba(56, 189, 248, 0.10);
# }

# .stat-card {
#     background: #111827;
#     border: 1px solid #334155;
#     border-radius: 16px;
#     padding: 18px;
#     text-align: center;
# }

# .stat-number {
#     font-size: 30px;
#     font-weight: 900;
#     color: #22c55e;
# }

# .stat-label {
#     font-size: 14px;
#     color: #94a3b8;
# }

# .stTextArea textarea {
#     background-color: #020617 !important;
#     color: #e5e7eb !important;
#     border: 1px solid #334155 !important;
#     border-radius: 14px !important;
# }

# .stButton button {
#     background: linear-gradient(90deg, #0284c7, #22c55e);
#     color: white !important;
#     border: none;
#     border-radius: 12px;
#     padding: 0.65rem 1.1rem;
#     font-weight: 700;
#     transition: 0.25s ease;
# }

# .stButton button:hover {
#     background: linear-gradient(90deg, #0369a1, #16a34a);
#     transform: scale(1.02);
#     color: white !important;
#     border: none;
# }

# div[data-testid="stAlert"] {
#     border-radius: 14px;
# }

# hr {
#     border-color: #334155;
# }
# </style>
# """, unsafe_allow_html=True)


# st.sidebar.markdown("## 🛠️ FixMind")
# st.sidebar.markdown("### Embedded AI Debugger")
# page = st.sidebar.radio("Navigation", ["🏠 Home", "📚 Memory History", "ℹ️ About"])

# for key, default in {
#     "problem": "",
#     "answer": "",
#     "memory_found": [],
#     "selected_memory": None,
#     "show_memory": False,
#     "show_ai_answer": False,
#     "saved": False,
# }.items():
#     if key not in st.session_state:
#         st.session_state[key] = default


# if page == "🏠 Home":
#     memories = load_memories()

#     st.markdown("""
#     <div class="hardware-card">
#         <h1>🛠️ FixMind</h1>
#         <h3>AI-Powered Embedded Systems Debugging Memory</h3>
#         <span class="feature-badge">Gemini AI</span>
#         <span class="feature-badge">Cognee Semantic Memory</span>
#         <span class="feature-badge">JSON Backup</span>
#         <span class="warning-badge">Hardware Debug Assistant</span>
#     </div>
#     """, unsafe_allow_html=True)

#     col1, col2, col3 = st.columns(3)

#     with col1:
#         st.markdown(f"""
#         <div class="stat-card">
#             <div class="stat-number">{len(memories)}</div>
#             <div class="stat-label">Stored Memories</div>
#         </div>
#         """, unsafe_allow_html=True)

#     with col2:
#         st.markdown("""
#         <div class="stat-card">
#             <div class="stat-number">AI</div>
#             <div class="stat-label">Debugging Engine</div>
#         </div>
#         """, unsafe_allow_html=True)

#     with col3:
#         cognee_status = "ON" if USE_COGNEE else "OFF"
#         st.markdown(f"""
#         <div class="stat-card">
#             <div class="stat-number">{cognee_status}</div>
#             <div class="stat-label">Cognee Memory</div>
#         </div>
#         """, unsafe_allow_html=True)

#     st.markdown("### 🔧 Describe Your Embedded Systems Problem")

#     problem_input = st.text_area(
#         "Examples: STM32 UART not transmitting, ESP32 WiFi not connecting, I2C device not detected",
#         height=150,
#         value=st.session_state.problem
#     )

#     if st.button("🚀 Ask FixMind"):
#         if problem_input.strip() == "":
#             st.warning("Please enter your problem.")
#         else:
#             st.session_state.problem = problem_input
#             st.session_state.answer = ""
#             st.session_state.memory_found = []
#             st.session_state.selected_memory = None
#             st.session_state.show_memory = False
#             st.session_state.show_ai_answer = False
#             st.session_state.saved = False

#             formatted_cognee = ""

#             if USE_COGNEE:
#                 with st.spinner("Searching Cognee memory..."):
#                     cognee_results = recall_with_cognee(problem_input)
#                     formatted_cognee = format_cognee_results(cognee_results)

#             if formatted_cognee:
#                 st.session_state.memory_found = [{
#                     "problem": "Cognee Semantic Memory Match",
#                     "date": "Retrieved from Cognee",
#                     "solution": formatted_cognee
#                 }]
#             else:
#                 st.session_state.memory_found = search_memory(problem_input)

#             if not st.session_state.memory_found:
#                 st.session_state.show_ai_answer = True

#     if st.session_state.memory_found and not st.session_state.show_ai_answer:
#         memory = st.session_state.memory_found[0]

#         st.markdown(f"""
#         <div class="memory-card">
#             <h3>🧠 Similar Engineering Memory Found</h3>
#             <p><b>Stored Problem:</b> {memory['problem']}</p>
#             <p><b>Saved:</b> {memory['date']}</p>
#             <p>This previous debugging session may help with your current hardware issue.</p>
#         </div>
#         """, unsafe_allow_html=True)

#         col1, col2 = st.columns(2)

#         with col1:
#             if st.button("👁 View Previous Fix"):
#                 st.session_state.selected_memory = memory
#                 st.session_state.show_memory = True
#                 st.session_state.show_ai_answer = False

#         with col2:
#             if st.button("✨ Generate New AI Solution"):
#                 st.session_state.selected_memory = None
#                 st.session_state.show_memory = False
#                 st.session_state.show_ai_answer = True
#                 st.session_state.answer = ""
#                 st.session_state.saved = False

#     if st.session_state.show_memory and st.session_state.selected_memory:
#         memory = st.session_state.selected_memory

#         st.markdown('<div class="response-card">', unsafe_allow_html=True)
#         st.markdown("## Previous Fix")
#         st.write(f"**Problem:** {memory['problem']}")
#         st.write(f"**Date:** {memory['date']}")
#         st.markdown(memory["solution"])
#         st.markdown('</div>', unsafe_allow_html=True)

#     if st.session_state.show_ai_answer:
#         if st.session_state.answer == "":
#             with st.spinner("FixMind is analyzing your hardware issue..."):
#                 try:
#                     st.session_state.answer = ask_gemini(st.session_state.problem)
#                 except Exception as e:
#                     st.error("Gemini connection failed.")
#                     st.code(str(e))

#         if st.session_state.answer:
#             st.success("✅ FixMind Response")

#             st.markdown('<div class="response-card">', unsafe_allow_html=True)
#             st.markdown(st.session_state.answer)
#             st.markdown('</div>', unsafe_allow_html=True)

#             st.divider()

#             if not st.session_state.saved:
#                 if st.button("💾 Mark as Solved and Save Memory"):
#                     json_saved = save_memory(
#                         st.session_state.problem,
#                         st.session_state.answer
#                     )

#                     cognee_saved = False

#                     if USE_COGNEE:
#                         with st.spinner("Saving to Cognee semantic memory..."):
#                             cognee_saved = remember_with_cognee(
#                                 st.session_state.problem,
#                                 st.session_state.answer
#                             )

#                     st.session_state.saved = True

#                     if USE_COGNEE and cognee_saved:
#                         st.success("Memory saved successfully in JSON + Cognee!")
#                     elif not USE_COGNEE:
#                         if json_saved:
#                             st.success("Memory saved successfully in JSON. Cognee is disabled.")
#                         else:
#                             st.info("This memory already exists in JSON.")
#                     else:
#                         if json_saved:
#                             st.warning("Saved in JSON. Cognee failed, but backup memory is safe.")
#                         else:
#                             st.info("This memory already exists in JSON.")
#             else:
#                 st.info("This solution is already saved.")


# elif page == "📚 Memory History":
#     st.markdown("""
#     <div class="hardware-card">
#         <h1>📚 Memory History</h1>
#         <h3>Previously solved embedded debugging sessions</h3>
#     </div>
#     """, unsafe_allow_html=True)

#     memories = load_memories()

#     if not memories:
#         st.info("No memories stored yet.")
#     else:
#         st.success(f"{len(memories)} debugging memories stored.")

#         for index, memory in enumerate(memories):
#             with st.expander(f"🧠 {index + 1}. {memory['problem']}"):
#                 st.write(f"**Date:** {memory['date']}")
#                 st.markdown(memory["solution"])

#                 if st.button("🗑 Delete Memory", key=f"delete_{index}"):
#                     delete_memory(index)
#                     st.success("Memory deleted successfully!")
#                     st.rerun()


# else:
#     st.markdown("""
#     <div class="hardware-card">
#         <h1>ℹ️ About FixMind</h1>
#         <h3>AI debugging memory for embedded systems engineers</h3>
#         <p>
#         FixMind helps engineers debug STM32, ESP32, Arduino, sensors,
#         UART, SPI, I2C, ADC, and hardware communication problems.
#         </p>
#         <span class="feature-badge">Gemini</span>
#         <span class="feature-badge">Cognee</span>
#         <span class="feature-badge">Streamlit</span>
#         <span class="feature-badge">GitHub Backup</span>
#     </div>
#     """, unsafe_allow_html=True)


#No.1 Working Code without UI
# import streamlit as st
# import google.generativeai as genai
# from dotenv import load_dotenv
# import os

# from memory.memory_manager import (
#     save_memory,
#     load_memories,
#     search_memory,
#     delete_memory,
# )

# from memory.cognee_memory import remember_with_cognee, recall_with_cognee

# load_dotenv()

# USE_COGNEE = os.getenv("USE_COGNEE", "false").lower() == "true"

# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# model = genai.GenerativeModel("gemini-2.5-flash")


# def ask_gemini(problem):
#     prompt = f"""
# You are FixMind, a senior Embedded Systems debugging assistant.

# User problem:
# {problem}

# Give a SHORT, practical debugging response.

# Use exactly this format:

# ### Possible Causes
# - Cause 1
# - Cause 2
# - Cause 3
# - Cause 4

# ### Step-by-Step Checks
# 1. Check ...
# 2. Verify ...
# 3. Test ...
# 4. Confirm ...

# ### Most Likely Fix
# Write the most likely fix in 2-3 lines.

# ### Prevention Tip
# Write one practical prevention tip.

# Rules:
# - Keep the answer concise.
# - Focus on STM32, ESP32, Arduino, UART, SPI, I2C, ADC, ESP32, sensors, embedded hardware.
# """
#     response = model.generate_content(prompt)
#     return response.text


# def format_cognee_results(results):
#     if not results:
#         return ""

#     invalid_phrases = [
#         "does not contain any information",
#         "does not contain information",
#         "provided context does not",
#         "no information about",
#         "cannot answer",
#         "not enough information",
#         "no relevant information",
#     ]

#     text = str(results).strip()

#     if any(phrase in text.lower() for phrase in invalid_phrases):
#         return ""

#     try:
#         if isinstance(results, list):
#             first = results[0]

#             if isinstance(first, dict):
#                 search_result = first.get("search_result", "")

#                 if isinstance(search_result, list) and search_result:
#                     result_text = str(search_result[0])
#                     if any(phrase in result_text.lower() for phrase in invalid_phrases):
#                         return ""
#                     return result_text

#                 if isinstance(search_result, str):
#                     if any(phrase in search_result.lower() for phrase in invalid_phrases):
#                         return ""
#                     return search_result

#     except Exception:
#         pass

#     return text


# st.set_page_config(page_title="FixMind", page_icon="🛠️", layout="wide")

# st.sidebar.title("🛠️ FixMind")
# page = st.sidebar.radio("Navigation", ["Home", "Memory History", "About"])

# for key, default in {
#     "problem": "",
#     "answer": "",
#     "memory_found": [],
#     "selected_memory": None,
#     "show_memory": False,
#     "show_ai_answer": False,
#     "saved": False,
# }.items():
#     if key not in st.session_state:
#         st.session_state[key] = default


# if page == "Home":
#     st.title("🛠️ FixMind")
#     st.subheader("Your Personal Engineering Memory")

#     st.write("""
# Describe your Embedded Systems problem below.

# Examples:
# - STM32 UART not transmitting
# - ESP32 WiFi not connecting
# - SPI communication failed
# - I2C device not detected
# """)

#     problem_input = st.text_area(
#         "Describe your debugging issue",
#         height=150,
#         value=st.session_state.problem
#     )

#     if st.button("Ask FixMind"):
#         if problem_input.strip() == "":
#             st.warning("Please enter your problem.")
#         else:
#             st.session_state.problem = problem_input
#             st.session_state.answer = ""
#             st.session_state.memory_found = []
#             st.session_state.selected_memory = None
#             st.session_state.show_memory = False
#             st.session_state.show_ai_answer = False
#             st.session_state.saved = False

#             formatted_cognee = ""

#             if USE_COGNEE:
#                 with st.spinner("Searching Cognee memory..."):
#                     cognee_results = recall_with_cognee(problem_input)
#                     formatted_cognee = format_cognee_results(cognee_results)

#             if formatted_cognee:
#                 st.session_state.memory_found = [{
#                     "problem": "Cognee Semantic Memory Match",
#                     "date": "Retrieved from Cognee",
#                     "solution": formatted_cognee
#                 }]
#             else:
#                 st.session_state.memory_found = search_memory(problem_input)

#             if not st.session_state.memory_found:
#                 st.session_state.show_ai_answer = True

#     if st.session_state.memory_found and not st.session_state.show_ai_answer:
#         memory = st.session_state.memory_found[0]
#         st.info("🧠 Similar debugging session found.")

#         st.markdown(f"**Previous Problem:** {memory['problem']}")
#         st.write(f"**Saved:** {memory['date']}")

#         col1, col2 = st.columns([1, 1])

#         with col1:
#             if st.button("👁 View Previous Fix"):
#                 st.session_state.selected_memory = memory
#                 st.session_state.show_memory = True
#                 st.session_state.show_ai_answer = False

#         with col2:
#             if st.button("✨ Generate New AI Solution"):
#                 st.session_state.selected_memory = None
#                 st.session_state.show_memory = False
#                 st.session_state.show_ai_answer = True
#                 st.session_state.answer = ""
#                 st.session_state.saved = False

#     if st.session_state.show_memory and st.session_state.selected_memory:
#         memory = st.session_state.selected_memory

#         st.markdown("## Previous Fix")
#         st.write(f"**Problem:** {memory['problem']}")
#         st.write(f"**Date:** {memory['date']}")
#         st.markdown(memory["solution"])

#     if st.session_state.show_ai_answer:
#         if st.session_state.answer == "":
#             with st.spinner("FixMind is thinking..."):
#                 try:
#                     st.session_state.answer = ask_gemini(st.session_state.problem)
#                 except Exception as e:
#                     st.error("Gemini connection failed.")
#                     st.code(str(e))

#         if st.session_state.answer:
#             st.success("FixMind Response")
#             st.markdown(st.session_state.answer)

#             st.divider()

#             if not st.session_state.saved:
#                 if st.button("✅ Mark as Solved and Save Memory"):
#                     json_saved = save_memory(
#                         st.session_state.problem,
#                         st.session_state.answer
#                     )

#                     cognee_saved = False

#                     if USE_COGNEE:
#                         with st.spinner("Saving to Cognee memory..."):
#                             cognee_saved = remember_with_cognee(
#                                 st.session_state.problem,
#                                 st.session_state.answer
#                             )

#                     st.session_state.saved = True

#                     if USE_COGNEE and cognee_saved:
#                         st.success("Memory saved successfully in JSON + Cognee!")
#                     elif not USE_COGNEE:
#                         if json_saved:
#                             st.success("Memory saved successfully in JSON. Cognee is disabled.")
#                         else:
#                             st.info("This memory already exists in JSON.")
#                     else:
#                         if json_saved:
#                             st.warning("Saved in JSON. Cognee memory failed, but JSON backup is safe.")
#                         else:
#                             st.info("This memory already exists in JSON.")
#             else:
#                 st.info("This solution is already saved.")


# elif page == "Memory History":
#     st.title("📚 Memory History")

#     memories = load_memories()

#     if not memories:
#         st.info("No memories stored yet.")
#     else:
#         st.success(f"{len(memories)} debugging memories stored.")

#         for index, memory in enumerate(memories):
#             with st.expander(f"{index + 1}. {memory['problem']}"):
#                 st.write(f"**Date:** {memory['date']}")
#                 st.markdown(memory["solution"])

#                 if st.button("🗑 Delete Memory", key=f"delete_{index}"):
#                     delete_memory(index)
#                     st.success("Memory deleted successfully!")
#                     st.rerun()


# else:
#     st.title("About FixMind")

#     st.write("""
# FixMind is an AI-powered debugging assistant for Embedded Systems engineers.

# It remembers previous debugging sessions and recalls similar past fixes using JSON backup and Cognee semantic memory.

# Developed for the WeMakeDevs Hackathon.
# """)
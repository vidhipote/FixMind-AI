# 🛠️ FixMind

> **AI-Powered Embedded Systems Debugging Assistant with Persistent Semantic Memory**

FixMind is an AI-powered debugging assistant designed for embedded systems engineers and students. It helps diagnose hardware and firmware issues using **Google Gemini AI** while leveraging **Cognee Cloud Semantic Memory** to recall previously solved debugging sessions. A local **JSON backup memory** ensures debugging knowledge is always available.

---

# 📌 Project Overview

Embedded systems debugging is often repetitive. Engineers frequently encounter the same issues such as UART communication failures, I2C device detection problems, SPI errors, GPIO configuration mistakes, and ADC signal issues.

FixMind reduces debugging time by:

- Searching previous debugging knowledge using **Cognee Semantic Memory**
- Reusing previously solved engineering solutions
- Generating new AI-powered debugging suggestions using **Gemini AI**
- Saving newly solved debugging sessions for future reuse

---

# 🚀 Features

- 🤖 Google Gemini AI powered debugging
- 🧠 Cognee Cloud Semantic Memory integration
- 💾 Local JSON backup memory
- 🔍 Automatic memory recall before AI generation
- 📚 Memory History management
- 🛠 Supports common embedded communication protocols
- 🌙 Modern Streamlit user interface
- ☁ Hybrid memory architecture (Cloud + Local)

---

# 🔌 Supported Hardware Debug Areas

- UART
- SPI
- I2C
- ADC
- GPIO

Supports debugging for:

- Arduino
- ESP32
- STM32
- Sensors
- Embedded peripherals

---

# 🧠 System Workflow

```text
User enters debugging problem
            │
            ▼
Search Cognee Semantic Memory
            │
     ┌──────┴──────┐
     │             │
Memory Found    No Memory
     │             │
     ▼             ▼
Show Previous   Generate New
Engineering Fix  using Gemini AI
     │             │
     └──────┬──────┘
            ▼
 Save Debug Solution
            │
            ▼
Store in:
• Cognee Cloud
• Local JSON Memory
```

---

# 🖼️ Application Screenshots

---

## 🏠 Home Page

> <img width="1918" height="863" alt="home" src="https://github.com/user-attachments/assets/dcf5ff85-15f8-4c85-9f16-448d88b43d24" />

---

## 🧠 Memory Recall


> <img width="1918" height="877" alt="memory recall (2)" src="https://github.com/user-attachments/assets/65d842bc-8fa6-4ee5-b5df-d1721177c01b" />



---

## 📖 Previous Engineering Fix

> <img width="1918" height="756" alt="previousfix" src="https://github.com/user-attachments/assets/4301b5d3-590b-4235-a50b-ad1d1661e1be" />


---

## 🤖 AI Generated Solution


> <img width="1918" height="872" alt="aigeneartedsolu" src="https://github.com/user-attachments/assets/ee43b223-b8c4-4f14-bac3-fc794a1dc081" />

---

## 📚 Memory History


> <img width="1918" height="876" alt="memory recall" src="https://github.com/user-attachments/assets/eff695fb-691e-4e00-b9df-984863c02094" />

---

## ☁ Cognee Cloud Memory


> <img width="1912" height="873" alt="cogneecloud" src="https://github.com/user-attachments/assets/7610bea2-59cc-4064-9e39-08ae58115c07" />

---

# 🛠 Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Backend |
| Streamlit | User Interface |
| Google Gemini AI | AI Debugging |
| Cognee Cloud | Semantic Memory |
| JSON | Local Backup Memory |
| GitHub | Version Control |

---

# 📁 Project Structure

```text
FixMind/
│
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
│
├── ai/
│   └── gemini.py
│
├── memory/
│   ├── memory_manager.py
│   ├── cognee_memory.py
│   └── memory_store.json
│
│
└── assets/
```

---

# ⚙ Installation

Clone the repository

```bash
git clone https://github.com/yourusername/FixMind.git

cd FixMind
```

Create virtual environment

```bash
python -m venv venv
```

Activate environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Variables

Create a `.env` file.

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY

USE_COGNEE=true

USE_COGNEE_CLOUD=true

COGNEE_API_BASE_URL=YOUR_BASE_URL

COGNEE_API_KEY=YOUR_API_KEY

COGNEE_TENANT_ID=YOUR_TENANT_ID

COGNEE_USER_ID=YOUR_USER_ID
```

**Do NOT upload `.env` to GitHub.**

---

# ▶ Run Application

```bash
streamlit run app.py
```

Application will start on

```
http://localhost:8501
```

---

# ☁ Cognee Semantic Memory

FixMind integrates with **Cognee Cloud** to store engineering debugging knowledge as semantic memories.

When a user submits a problem:

1. Cognee searches for similar debugging sessions.
2. If a match exists, the previous engineering solution is displayed.
3. If no match exists, Gemini AI generates a new debugging solution.
4. The solution can then be saved to both:
   - Cognee Cloud
   - Local JSON Backup

---

# 💾 Local JSON Backup

Each saved debugging session is also stored locally.

Benefits:

- Offline backup
- Faster retrieval
- Easy management
- Delete support from Memory History

---

# 🧪 Example Debugging Problems

```
STM32 UART not transmitting

ESP32 WiFi not connecting

I2C device not detected

Arduino isn't transmitting data

SPI communication failed

ADC values are fluctuating

GPIO output pin not changing state
```

---

# 📦 Dependencies

Install using:

```bash
pip install -r requirements.txt
```

Main libraries:

- streamlit
- google-generativeai
- python-dotenv
- cognee

---

# 🎯 Future Improvements

- Multiple LLM support
- Voice-based debugging assistant
- Image-based hardware diagnosis
- Circuit diagram analysis
- Team shared memory
- PCB debugging support
- PDF debugging report generation
- Embedded project knowledge graphs

---

# 🏆 Hackathon Project

Developed as an AI-powered debugging assistant demonstrating:

- Semantic Memory
- AI-assisted Debugging
- Embedded Systems Knowledge Management
- Cloud Memory Retrieval
- Persistent Engineering Knowledge

---

# 👩‍💻 Author

**Vidhi Pote**

Embedded Systems | AI | Streamlit | Cognee Cloud

---

# ⭐ If you found this project useful

Give this repository a ⭐ on GitHub.

---

# 📜 License

This project is developed for educational and hackathon purposes.

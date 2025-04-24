# Nugget_chatbot

**Nugget Chatbot** is a smart, lightweight, and customizable AI chatbot built to streamline conversations, provide automated assistance, and improve user interaction across various platforms. It's built using modern technologies and can be deployed easily in just a few steps.

## ✨ Features

- 💬 Natural Language Understanding using OpenAI API (or any preferred LLM)
- ⚡ Lightweight and fast response time
- 🛠️ Easy to customize and extend
- 🔌 Can be integrated into websites, apps, or used as a standalone assistant
- 🔐 Secure with environment-based API access

---

## 📦 Installation

Follow the steps below to set up and run Nugget Chatbot locally:

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/nugget-chatbot.git
cd nugget-chatbot
2. Set Up a Virtual Environment (Optional but Recommended)
bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
3. Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
4. Configure Environment Variables
Create a .env file in the root directory and add your credentials:

env
Copy
Edit
OPENAI_API_KEY=your_openai_api_key
You may also include other environment variables if required by your setup (e.g., API_HOST, DEBUG, etc.).

5. Run the Chatbot
bash
Copy
Edit
python app.py

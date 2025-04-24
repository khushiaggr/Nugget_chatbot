import os
import json
import gradio as gr
import google.generativeai as genai
from typing import List, Dict, Any

# Configure the Gemini API
genai.configure(api_key="AIzaSyCG376vlsNmhpjA6uj4yrh0nrq1uJywaZM")

# Load restaurant data
def load_restaurant_data() -> List[Dict[str, Any]]:
    try:
        with open("restaurants.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"Successfully loaded data for {len(data)} restaurants")
        return data
    except Exception as e:
        print(f"Error loading restaurant data: {e}")
        return []

# Initialize restaurant data
restaurant_data = load_restaurant_data()

# Create a Gemini model instance
model = genai.GenerativeModel('gemini-pro')

def create_restaurant_system_prompt() -> str:
    """Create a system prompt that includes restaurant data"""
    restaurant_context = "Restaurant information:\n"
    
    for i, restaurant in enumerate(restaurant_data):
        restaurant_context += f"\nRestaurant {i+1}: {restaurant.get('name', 'Unknown')}\n"
        restaurant_context += f"Location: {restaurant.get('location', 'Unknown')}\n"
        restaurant_context += f"Hours: {restaurant.get('operating_hours', 'Unknown')}\n"
        restaurant_context += f"Contact: {restaurant.get('contact_info', 'Unknown')}\n"
        
        # Add a sample of menu items (limit to avoid context length issues)
        menu_items = restaurant.get('menu', [])
        restaurant_context += "Menu items (sample):\n"
        for item in menu_items[:5]:  # Limit to 5 items per restaurant
            restaurant_context += f"- {item.get('item', 'Unknown')}: {item.get('price', 'Unknown')}"
            if item.get('tags'):
                restaurant_context += f" [{', '.join(item.get('tags', []))}]"
            restaurant_context += "\n"
            
    system_prompt = f"""You are a helpful restaurant assistant chatbot. Your job is to help users find 
    restaurants, dishes, and answer food-related questions. Be concise and friendly.
    
    {restaurant_context}
    
    When recommending restaurants or dishes:
    1. Focus on the restaurants in your database
    2. Suggest specific menu items when appropriate
    3. Mention any relevant dietary tags (vegetarian, vegan, gluten-free, spicy)
    4. Provide price information when available
    
    If users ask for something outside your knowledge, politely inform them that 
    you can only provide information about the restaurants in your database.
    """
    return system_prompt

# System prompt with restaurant data
SYSTEM_PROMPT = create_restaurant_system_prompt()

# Chat history for Gradio
chat_history = []

def process_message(message, history):
    """Process user message with Gemini and return response"""
    # Prepare chat history for Gemini
    gemini_history = []
    for human, assistant in history:
        gemini_history.append({"role": "user", "parts": [human]})
        gemini_history.append({"role": "model", "parts": [assistant]})
    
    # Add the system prompt to provide context
    gemini_messages = [
        {"role": "user", "parts": [SYSTEM_PROMPT]},
        {"role": "model", "parts": ["I understand. I'll be a restaurant assistant chatbot, providing information about the restaurants in my database."]},
    ]
    
    # Add chat history
    gemini_messages.extend(gemini_history)
    
    # Add current message
    gemini_messages.append({"role": "user", "parts": [message]})
    
    try:
        # Get response from Gemini
        response = model.generate_content(gemini_messages)
        return response.text
    except Exception as e:
        print(f"Error generating response: {e}")
        return "I'm having trouble connecting to my brain right now. Could you try again in a moment?"

# Create Gradio Interface
with gr.Blocks(css="styles.css", theme="dark") as gradio_app:
    gr.HTML("""
    <div style="text-align: center; margin-bottom: 10px;">
        <h1 style="color: #FFD166;">Restaurant Buddy API Endpoint</h1>
        <p>This Gradio app serves as the backend API for the Restaurant Buddy chatbot.</p>
    </div>
    """)
    
    chatbot = gr.Chatbot(
        [],
        elem_id="chatbot",
        avatar_images=("https://api.dicebear.com/7.x/avataaars/svg?seed=user", "https://api.dicebear.com/7.x/bottts/svg?seed=restaurant"),
    )
    msg = gr.Textbox(placeholder="Ask about restaurants, menus, or dishes...")
    clear = gr.Button("Clear")

    msg.submit(process_message, [msg, chatbot], [chatbot, msg], queue=False)
    clear.click(lambda: None, None, chatbot, queue=False)
    
    gr.HTML("""
    <div style="text-align: center; margin-top: 20px; padding: 10px; border-top: 1px solid rgba(255, 255, 255, 0.1);">
        <p style="font-size: 0.8em;">Powered by Gemini Pro 2.5</p>
    </div>
    """)

    # Add a route for API access
    @gradio_app.load(api_name="chat")
    def api_chat(message, history=[]):
        response = process_message(message, history)
        return response

# Start the server
if __name__ == "__main__":
    print("Starting Restaurant Buddy backend server...")
    print("Loading restaurant data...")
    restaurant_data = load_restaurant_data()  
    print("Starting Gradio server...")
    gradio_app.launch(server_name="0.0.0.0", server_port=7860, share=True)

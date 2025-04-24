/nugget_chatbot/script.js
document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const clearButton = document.getElementById('clear-chat');
    const suggestionChips = document.querySelectorAll('.chip');
    
    // Restaurant data and chat history
    let restaurantData = [];
    let chatHistory = [];
    
    // Backend API URL - adjust if needed
    const API_URL = 'http://localhost:7860/api/chat';
    
    // Function to add a message to the chat
    function addMessage(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = isUser ? 'message user-message' : 'message bot-message';
        
        // Create avatar
        const avatar = document.createElement('div');
        avatar.className = isUser ? 'avatar user-avatar' : 'avatar bot-avatar';
        
        if (isUser) {
            avatar.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M20 21V19C20 16.7909 18.2091 15 16 15H8C5.79086 15 4 16.7909 4 19V21" stroke="#06D6A0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M12 11C14.2091 11 16 9.20914 16 7C16 4.79086 14.2091 3 12 3C9.79086 3 8 4.79086 8 7C8 9.20914 9.79086 11 12 11Z" stroke="#06D6A0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
        } else {
            avatar.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 15C15.866 15 19 11.866 19 8C19 4.13401 15.866 1 12 1C8.13401 1 5 4.13401 5 8C5 11.866 8.13401 15 12 15Z" stroke="#FFD166" stroke-width="2"/><path d="M12 15V23" stroke="#FFD166" stroke-width="2"/><path d="M8 19H16" stroke="#FFD166" stroke-width="2"/></svg>';
        }
        
        // Create message content
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // Format the content - handle markdown-style formatting
        const formattedContent = formatMessage(content);
        messageContent.innerHTML = formattedContent;
        
        // Assemble message
        if (isUser) {
            messageDiv.appendChild(messageContent);
            messageDiv.appendChild(avatar);
        } else {
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(messageContent);
        }
        
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Add to history if not already there
        if (isUser) {
            chatHistory.push(["user", content]);
        } else if (chatHistory.length === 0 || chatHistory[chatHistory.length - 1][0] !== "bot") {
            chatHistory.push(["bot", content]);
        }
    }
    
    // Simple formatter for text (handles basic markdown)
    function formatMessage(text) {
        // Convert links
        let formatted = text.replace(
            /\[(.*?)\]\((.*?)\)/g, 
            '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>'
        );
        
        // Convert bold
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert italic
        formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Convert newlines to <br>
        formatted = formatted.replace(/\n/g, '<br>');
        
        // Wrap in paragraph
        return `<p>${formatted}</p>`;
    }
    
    // Function to handle user input
    async function handleUserInput() {
        const userMessage = userInput.value.trim();
        if (userMessage === '') return;
        
        // Display user message
        addMessage(userMessage, true);
        
        // Clear input field
        userInput.value = '';
        
        // Show typing indicator
        showTypingIndicator();
        
        try {
            // Call API
            const response = await fetchBotResponse(userMessage);
            
            // Remove typing indicator
            removeTypingIndicator();
            
            // Display bot response
            addMessage(response);
        } catch (error) {
            // Remove typing indicator
            removeTypingIndicator();
            
            console.error('Error getting response:', error);
            addMessage("Sorry, I'm having trouble connecting to my brain right now. Could you try again in a moment?");
        }
    }
    
    // Function to show typing indicator
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message typing-indicator';
        typingDiv.id = 'typing-indicator';
        
        const avatar = document.createElement('div');
        avatar.className = 'avatar bot-avatar';
        avatar.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 15C15.866 15 19 11.866 19 8C19 4.13401 15.866 1 12 1C8.13401 1 5 4.13401 5 8C5 11.866 8.13401 15 12 15Z" stroke="#FFD166" stroke-width="2"/><path d="M12 15V23" stroke="#FFD166" stroke-width="2"/><path d="M8 19H16" stroke="#FFD166" stroke-width="2"/></svg>';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        content.innerHTML = '<div class="dots"><span></span><span></span><span></span></div>';
        
        typingDiv.appendChild(avatar);
        typingDiv.appendChild(content);
        
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Function to remove typing indicator
    function removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    // Function to fetch response from the API
    async function fetchBotResponse(message) {
        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    history: chatHistory.map(item => [item[1], ""]) // Format history for API
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            return data.data;
        } catch (error) {
            console.error('API Error:', error);
            
            // Fallback to local processing if API fails
            return processBotResponse(message);
        }
    }
    
    // Fallback local response processor
    function processBotResponse(message) {
        message = message.toLowerCase();
        
        if (message.includes('hello') || message.includes('hi') || message.includes('hey')) {
            return "Hello! How can I help you today with food or restaurant questions?";
        } 
        else if (message.includes('menu')) {
            return "I can help you find menu information. Which restaurant are you interested in?";
        }
        else if (message.includes('vegetarian') || message.includes('veg ') || message.includes('vegan')) {
            return "Looking for vegetarian options? I can suggest several restaurants with great vegetarian menus. Would you like me to list some options?";
        }
        else if (message.includes('pizza')) {
            return "Pizza is always a good choice! I know several great pizza places. Would you like recommendations based on style or location?";
        }
        else if (message.includes('spicy')) {
            return "If you're looking for spicy food, I can suggest some restaurants that offer dishes with different heat levels. Any specific cuisine you prefer?";
        }
        else if (message.includes('thank')) {
            return "You're welcome! Let me know if you need anything else.";
        }
        else {
            return "I'm not sure I understand. Are you looking for restaurant recommendations, menu information, or something else food-related?";
        }
    }
    
    // Event listeners
    sendButton.addEventListener('click', handleUserInput);
    
    userInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            handleUserInput();
        }
    });
    
    clearButton.addEventListener('click', function() {
        // Keep only the first bot message
        while (chatMessages.children.length > 1) {
            chatMessages.removeChild(chatMessages.lastChild);
        }
        
        // Clear chat history
        chatHistory = [];
    });
    
    suggestionChips.forEach(chip => {
        chip.addEventListener('click', function() {
            userInput.value = chip.textContent;
            handleUserInput();
        });
    });
    
    // Focus input on load
    userInput.focus();
    
    // Function to load restaurant data
    async function loadRestaurantData() {
        try {
            const response = await fetch('restaurants.json');
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error loading restaurant data:', error);
            return [];
        }
    }
    
    // Initialize by loading restaurant data
    loadRestaurantData().then(data => {
        restaurantData = data;
        console.log('Restaurant data loaded!');
    });
});
from src.ai_service import generate_response, load_model

class ConversationManager:
    def __init__(self):
        self.conversations = {}
        self.model = load_model()
    
    def start_conversation(self, user_id):
        """Initialize a new conversation for a user."""
        if user_id not in self.conversations:
            self.conversations[user_id] = []
    
    def add_message(self, user_id, role, message):
        """Add a message to the user's conversation history."""
        if user_id not in self.conversations:
            self.start_conversation(user_id)
        self.conversations[user_id].append({"role": role, "message": message})
    
    def get_conversation(self, user_id):
        """Retrieve the conversation history of a user."""
        return self.conversations.get(user_id, [])
    
    def clear_conversation(self, user_id):
        """Clear the conversation history of a user."""
        if user_id in self.conversations:
            self.conversations[user_id] = []

    def process_user_query(self, user_id, query):
        """Process user query and generate AI response."""
        self.add_message(user_id, "user", query)
        response = generate_response(self.model, query)
        self.add_message(user_id, "AI", response)
        return response

# Example usage:
if __name__ == "__main__":
    conv_manager = ConversationManager()
    user = "user_123"
    conv_manager.start_conversation(user)
    user_input = "Hello, AI!"
    ai_response = conv_manager.process_user_query(user, user_input)
    print(conv_manager.get_conversation(user))
import openai


class OpenAIAgent:

    def __init__(self, api_key):
        openai.api_key = api_key
        self.conversations = {}

    def process_message(self, user_id: str, message: str) -> str:
        # If user is new, start a new conversation
        if user_id not in self.conversations:
            self.conversations[user_id] = [{
                "role": "system",
                "content": "The assistant is helpful, creative, smart, very friendly and accurate.",
            }]

        # Add user's message to the conversation history
        self.conversations[user_id].append({"role": "user", "content": message})

        # Retrieve AI's response from OpenAI API
        response = self.get_ai_response(self.conversations[user_id])

        # Add AI's response to the conversation history
        self.conversations[user_id].append({"role": "assistant", "content": response})

        # Return AI's response
        return response

    def get_ai_response(self, conversation: list) -> str:
        # Generate AI's response using OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation,
            temperature=0.8,
            max_tokens=150,
            stop=["assistant", "user"]
        )

        # Extract AI's response from the API response
        return response.choices[0].message.content.strip()

    def reset_context(self, user_id: str):
        if user_id in self.conversations:
            del self.conversations[user_id]

# TODO: save chatGPT context to database

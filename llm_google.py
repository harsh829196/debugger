
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY is missing from .env")

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=api_key,
    max_retries=1,
)

# Store conversation history
chat_history = []

print("\n🤖 Gemini Terminal Chat")
print("Type 'exit' or 'quit' to stop.\n")

while True:
    try:
        user_input = input("You: ").strip()

        if user_input.lower() in ("exit", "quit"):
            print("Gemini: Goodbye!")
            break

        if not user_input:
            continue

        # Add the user's message
        chat_history.append(HumanMessage(content=user_input))

        # Send the conversation history
        response = llm.invoke(chat_history)

        # Display Gemini's response
        print(f"\nGemini: {response.text}\n")

        # Save the assistant's response
        chat_history.append(
            AIMessage(content=response.content)
        )

    except KeyboardInterrupt:
        print("\nGemini: Chat stopped.")
        break

    except Exception as e:
        print(f"\nError: {e}\n")
        # Remove the unanswered user message
        if chat_history and isinstance(chat_history[-1], HumanMessage):
            chat_history.pop()

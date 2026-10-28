
import os
from getpass import getpass
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
load_dotenv()
# Enter your Groq API key
api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=api_key,
    temperature=0.7,
)

chat_history = []

print("\nLlama Terminal Chat")
print("Type 'exit' or 'quit' to stop.\n")

while True:
    try:
        user_input = input("You: ").strip()

        if user_input.lower() in ("exit", "quit"):
            print("Llama: Goodbye!")
            break

        if not user_input:
            continue

        chat_history.append(HumanMessage(content=user_input))
        response = llm.invoke(chat_history)

        # Print only the assistant's text
        print(f"\nLlama: {response.content}\n")

        chat_history.append(AIMessage(content=response.content))

    except KeyboardInterrupt:
        print("\nGoodbye!")
        break

    except Exception as e:
        print(f"\nError: {e}\n")
        if chat_history and isinstance(chat_history[-1], HumanMessage):
            chat_history.pop()

from chatbot import Chatbot
from langchain_openai import ChatOpenAI

def main():

   # Set up the API key and initialize the model
    API = "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"
    model = ChatOpenAI(model="gpt-4o-2024-08-06", openai_api_key=API)
    chatbot = Chatbot(model)

    for i in range(5):
        answer = chatbot.chat(input('CHAT: '), API)
        print(answer)
    chatbot.save_conversation()
main()
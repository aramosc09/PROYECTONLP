import os
os.environ['USER_AGENT'] = 'myagent'
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain_community.document_loaders import PyPDFLoader
from chromadb import Client



class Translator:
    def __init__(self, model):
        self.model = model
        self.client = Client()
        self.data_path = "supported_languages/spanish_french.pdf"
        print("Traductor Initialized")

    def answer(self, human_query, api):
        all_documents = []

        if os.path.exists(self.data_path):
            # Cargar el archivo PDF
            loader = PyPDFLoader(self.data_path)
            data = loader.load()
            all_documents.extend(data)  # Añadimos los documentos cargados a la lista

            # Dividimos todos los documentos en trozos
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
            all_splits = text_splitter.split_documents(all_documents)

            # Creamos el vectorstore a partir de los documentos divididos
            vectorstore = Chroma.from_documents(
                documents=all_splits,
                embedding=OpenAIEmbeddings(api_key=api),
                client=Client()
            )

            # k is the number of chunks to retrieve
            retriever = vectorstore.as_retriever(k=4)

            docs = retriever.invoke(human_query)

            SYSTEM_TEMPLATE = """
Traduce el query del usuario a {language}.
Si el query no está en español responde "No sé"
Traduce en base al contexto proporcionado:

<provided context>
{context}
</provided context>
            """

            question_answering_prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        SYSTEM_TEMPLATE,
                    ),
                    MessagesPlaceholder(variable_name="messages"),
                ]
            )

            document_chain = create_stuff_documents_chain(self.model, question_answering_prompt)

            answer = document_chain.invoke(
                {
                    "context": docs,
                    "language": "francés",
                    "messages": [
                        HumanMessage(content=human_query)
                    ],
                }
            )
            return answer
        else:
            print(f"Archivo {self.data_path} no encontrado.")
            return "Error: El archivo PDF no fue encontrado."


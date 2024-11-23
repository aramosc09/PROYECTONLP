from flask import Flask, render_template, request, session
from flask_session import Session
from translator import Translator
from chatbot import Chatbot
from langchain_openai import ChatOpenAI

# Configuración de Flask
app = Flask(__name__)
app.secret_key = "mysecretkey"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configuración del modelo LLM
API_KEY = "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"  # Reemplaza con tu clave de OpenAI
model = ChatOpenAI(model="gpt-4", openai_api_key=API_KEY)

# Instanciar clases
translator = Translator(model)
chatbot = Chatbot(model)

@app.route("/", methods=["GET", "POST"])
def home():
    if "history" not in session:
        session["history"] = []  # Inicializa el historial si no existe

    if request.method == "POST":
        user_query = request.form.get("query")
        if user_query:
            try:
                # Obtener la traducción del chatbot
                response = chatbot.chat(user_query, API_KEY)

                # Guardar entrada y traducción en el historial
                session["history"].append({"user": user_query, "ai": response})
                print(session["history"])
                session.modified = True
            except Exception as e:
                session["history"].append({"user": user_query, "ai": f"Error: {str(e)}"})

    # Pasar historial al template
    return render_template("index.html", history=session["history"])

@app.route("/delete", methods=["POST"])
def delete_entry():
    """
    Elimina una entrada del historial basada en el índice enviado desde el formulario.
    """
    index = int(request.form.get("index"))
    if "history" in session and 0 <= index < len(session["history"]):
        session["history"].pop(index)
        session.modified = True
    return render_template("index.html", history=session["history"])

if __name__ == "__main__":
    app.run(debug=True)
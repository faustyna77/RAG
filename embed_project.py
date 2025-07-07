import json
import faiss
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2

# Inicjalizacja aplikacji i środowiska
app = FastAPI()
load_dotenv()

# Globalne zmienne
data = []
index = None
model = SentenceTransformer("all-MiniLM-L6-v2")

# Połączenie z bazą
def connect_database():
    conn = psycopg2.connect(os.getenv('string'))
    return conn

# Odświeżenie danych i stworzenie embeddings
def load_and_embed():
    global data, index

    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM "Projects"')
    rows = cursor.fetchall()

    projects = []
    for row in rows:
        project_data = {
            "title": row[1],
            "description": row[2],
            "category": row[6],
            "text": row[1] + ' ' + row[2]
        }
        projects.append(project_data)

    with open('projects.json', 'w') as f:
        json.dump(projects, f, indent=4)

    data = projects
    texts = [item["text"] for item in data]
    embeddings = model.encode(texts, show_progress_bar=True)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

# Pierwsze załadowanie przy starcie
load_and_embed()

# Klient OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("API_KEY")
)

class Query(BaseModel):
    question: str

# Główne API
@app.post("/ask")
def ask_question(query: Query):
    embedding = model.encode([query.question])
    _, I = index.search(embedding, k=1)
    project = data[I[0][0]]

    prompt = f"""Odpowiedz na pytanie na podstawie poniższych informacji o projekcie.
Nie zgaduj, jeśli nie masz wystarczającej informacji – powiedz, że nie wiesz. 
Pamiętaj, że wszystkie projekty na tej stronie są własnością Faustyny Misiura.

Tytuł: {project['title']}
Opis: {project['description']}
Kategoria: {project['category']}

Pytanie: {query.question}
"""

    response = client.chat.completions.create(
        model="openrouter/cypher-alpha:free",
        messages=[{"role": "user", "content": prompt}]
    )

    return {"response": response.choices[0].message.content}

# Endpoint do odświeżania danych
@app.get("/refresh")
def refresh_data():
    load_and_embed()
    return {"status": "Odświeżono dane i embeddings"}

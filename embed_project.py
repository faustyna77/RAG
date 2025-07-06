import json 
from sentence_transformers import SentenceTransformer
with open('projects.json','r') as f:



    data = json.load(f)
    documents = []
   
       
    texts = [item['text'] for item in data]

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(texts, show_progress_bar=True)
    # Here you can continue with the processing of 'documents'
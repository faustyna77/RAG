import psycopg2
from psycopg2 import sql
import json
from dotenv import load_dotenv
import os
import fastapi
from fastapi import FastAPI
from pydantic import BaseModel
load_dotenv()
connection_string=os.getenv('string')
def connect_database():
    
    conn = psycopg2.connect(
           connection_string
        )
    return conn
connection=connect_database()
cursor=connection.cursor()

cursor.execute('SELECT * FROM "Projects"')

rows = cursor.fetchall()

projects=[]
for row in rows:
    
    data={
        "title":row[1],
        "description":row[2],
        "category":row[6],
        "text":row[1]+''+row[2]
    }
    projects.append(data)

with open('projects.json','w')as f:
    f.write(json.dumps(projects,indent=4))

with open('projects.json','r') as f:
    data = json.load(f)
    documents = []
    for item in data:
        document={
            "title":item['title'],
            "description":item['description'],
            "category":item['category'],
            "text":item['text']
        }
        documents.append(document)
    print(documents)
    # uzupełnij to poniżej



    

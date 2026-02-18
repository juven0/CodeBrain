import getpass
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google API key: ")

def embeddAnswer( answer : str):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vector = embeddings.embed_query(answer)
    return vector


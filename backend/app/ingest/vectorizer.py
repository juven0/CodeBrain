import os
import getpass
from dotenv import load_dotenv
from google import genai
from google.genai import types
from langchain_google_genai import GoogleGenerativeAIEmbeddings


class GeminiEmbedder:
    def __init__(self, model: str = "models/gemini-embedding-001"):
        load_dotenv()

        if not os.getenv("GOOGLE_API_KEY"):
            os.environ["GOOGLE_API_KEY"] = getpass.getpass(
                "Enter your Google API key: "
            )

        self.model = model
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=self.model
            )
        self.client = genai.Client()

    def embed_document(self, text: str) -> list[float]:
        return self.client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(output_dimensionality=768)
        )

    def embed_query(self, query: str) -> list[float]:
        return self.embeddings.embed_query(query)
    
    def dimension(self) -> int:
        return len(self.embed_query("test"))

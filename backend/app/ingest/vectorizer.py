import os
import getpass
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings


class GeminiEmbedder:
    def __init__(self, model: str = "models/gemini-embedding-001"):
        load_dotenv()

        if not os.getenv("GOOGLE_API_KEY"):
            os.environ["GOOGLE_API_KEY"] = getpass.getpass(
                "Enter your Google API key: "
            )

        self.model = model
        self.embeddings = GoogleGenerativeAIEmbeddings(model=self.model)

    def embed_document(self, text: str) -> list[float]:
        return self.embeddings.embed_documents([text])[0]

    def embed_query(self, query: str) -> list[float]:
        return self.embeddings.embed_query(query)

from to_embeding import RepositoryReader
from js_chunk_adaptor import JSChunkAdaptor
from vecltor_storage import PineconeVectorStore
from huggingface_hub import InferenceClient
import os 

REPO_PATH = "../WorldWise-RESTful-API"
JS_FILES = [".js"]

def process():
    repoReader = RepositoryReader()
    storage = PineconeVectorStore()

    files = repoReader.read_repo(REPO_PATH)

    for file in files :
        print(file)
        if any(file.endswith(ext) for ext in JS_FILES):
            jsAdaptor = JSChunkAdaptor(file)
            code = repoReader.read_file(file)
            chunks = jsAdaptor.normalize(code)
            storage.upsert_chunks(chunks)

def search(query):
    storage = PineconeVectorStore()
    context = storage.query(query)
    c = f"Contexte extrait du code :{context}"
    q = f"Question :{query}"
    i = f"""Instructions pour la réponse :
        1. Fournis une réponse claire et concise.
        2. Explique les fonctions, classes, paramètres ou imports si nécessaire.
        3. Ne fais aucune supposition en dehors du contexte.
        4. Si la question concerne plusieurs fonctions ou fichiers, structure la réponse avec des titres.
        5. Ajoute éventuellement un exemple d'utilisation si pertinent.

        Réponse :"""

    hf_token = os.getenv("HF_API_TOKEN")
    client = InferenceClient(api_key=hf_token)

    stream = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "Tu es software engineer senior expert en code JavaScript. Ton rôle est de répondre aux questions en utilisant uniquement le contexte fourni ci-dessous. Si l'information n'est pas dans le contexte, répond honnêtement que tu ne sais pas."
            },
            {
                "role": "user",
                "content": c+ "\n" + q +"\n"+ i
            }
        ],
        stream=True
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


#process()
search("quelle point je doit ameliorer pour une meilleur gestion du user")


from to_embeding import RepositoryReader
from js_chunk_adaptor import JSChunkAdaptor
from vecltor_storage import PineconeVectorStore

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

process()


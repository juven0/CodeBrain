import hashlib
import os
from typing import List
from ingest.js_chunk_adaptor import JSChunkAdapter

SUPORTED_EXT = [".js"]

def read_repos(path : str):
    files: List[str] = []
    for root, dirs, filenames in os.walk(path):
        for file in filenames: 
            if any(file.endswith(ext) for ext in SUPORTED_EXT):
                files.append(os.path.join(root,file))
    
    return files

def read_file(file_path):
    with open(file_path, "r", encoding="utf8") as f:
        return f.read()

def compute_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

REPO_PATH = "../WorldWise-RESTful-API"

files = read_repos(REPO_PATH)

code = ""
for f in files:
    if "auth.service.js" in f:
        code = read_file(f)
print(code)

JS_adaptor = JSChunkAdapter("test")
chunks = JS_adaptor.normalize(code)

print(chunks)

import hashlib
import os
from typing import List
from chunk import Chunk
from js_chunk_adaptor import JSChunkAdaptor

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
    if "service.js" in f:
        code = read_file(f)

JS_adaptor = JSChunkAdaptor("test")
chunks = JS_adaptor.normalize(code)
for ch in chunks:
    print(ch.to_embedding())

import os
from typing import List
from chunk import Chunk
from js_chunk_adaptor import JSChunkAdaptor


class RepositoryReader:

    SUPPORTED_EXT = [".js"]

    def __init__(self):
        pass

    def read_repo(self, repo_path) -> List[str]:
        files: List[str] = []

        for root, dirs, filenames in os.walk(repo_path):
            for file in filenames:
                if any(file.endswith(ext) for ext in self.SUPPORTED_EXT):
                    files.append(os.path.join(root, file))

        return files

    def read_file(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf8") as f:
            return f.read()
 

# REPO_PATH = "../WorldWise-RESTful-API"

# files = read_repos(REPO_PATH)

# code = ""
# for f in files:
#     if "service.js" in f:
#         code = read_file(f)

# JS_adaptor = JSChunkAdaptor("test")
# chunks = JS_adaptor.normalize(code)
# for ch in chunks:
#     print(ch.to_embedding())

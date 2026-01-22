from typing import List
from backend.app.ingest.chunk import Chunk
from js_ingest import JavaScriptAnalyzer


class JS_chunk_adaptor:
    def __init__(self, file_path):
        self.js_analizer = JavaScriptAnalyzer()
        self.file_path = file_path
    
    def normalize(self, code)->List[Chunk]:
        chunks: List[Chunk] = []
        parsed_js = self.js_analizer.analyze(code)

        imports = parsed_js.get("imports")
        exports = parsed_js.get("exports")

        for fn in parsed_js.get("function", []):
            chunks.append(Chunk(imports=imports)
            )
        
        for ar in parsed_js.get("arrow_functions", []):
            chunks.append(Chunk(imports=imports))
        
        for cl in parsed_js.get("classes", []):
            chunks.append(Chunk(imports=imports))
        
        return chunks
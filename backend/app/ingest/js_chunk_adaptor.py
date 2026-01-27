from typing import List
from chunk import Chunk
from js_ingest import JavaScriptAnalyzer


class JSChunkAdaptor:
    def __init__(self, file_path):
        self.js_analizer = JavaScriptAnalyzer()
        self.file_path = file_path
    
    def normalize(self, code)->List[Chunk]:
        chunks: List[Chunk] = []
        parsed_js = self.js_analizer.analyze(code)

        imports = parsed_js.get("imports")
        exports = parsed_js.get("exports")

        for fn in parsed_js.get("functions", []):
            chunks.append(Chunk(
                    imports=imports, 
                    name=fn.get("name"),
                    type=fn.get("type"),
                    language=fn.get("language"),
                    params=fn.get("params"),
                    code=fn.get("code"),
                    path= self.file_path))
        
        for ar in parsed_js.get("arrow_functions", []):
            chunks.append(
                Chunk(
                    imports=imports,
                    name=ar.get("name"),
                    type=ar.get("type"),
                    language=ar.get("language"),
                    params=ar.get("params"),
                    code=ar.get("code"),
                    path= self.file_path))
        
        for cls in parsed_js.get("classes", []):
            metadata = {}

            if "methods" in cls:
                metadata["methods"] = cls["methods"]

            chunks.append(
                Chunk(
                    imports=imports,
                    name=fn.get("name"),
                    type=fn.get("type"),
                    language=fn.get("language"),
                    params=fn.get("params"),
                    code=fn.get("code"),
                    path= self.file_path,
                    metadata=metadata
                    ))
        
        return chunks
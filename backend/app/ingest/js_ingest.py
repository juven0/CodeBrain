from tree_sitter import Parser, Language
import tree_sitter_javascript as ts_js


class JavaScriptAnalyzer:
    def __init__(self):
        self.js_language = Language(ts_js.language())
        self.parser = Parser(self.js_language)
    
    def parse(self, code):
        """Parse JavaScript code and return the AST root node."""
        if isinstance(code, str):
            code = code.encode('utf-8')
        tree = self.parser.parse(code)
        return tree.root_node, code
    
    @staticmethod
    def node_text(code, node):
        return code[node.start_byte:node.end_byte].decode("utf-8")
    
    def extract_imports(self, root, code):
        imports = []

        def walk(node):
            if node.type == "import_statement":
                for c in node.children:
                    if c.type == "string":
                        imports.append(self.node_text(code, c).strip("'\""))
            for child in node.children:
                walk(child)
        
        walk(root)
        return imports
    
    def extract_calls(self, node, code):
        calls = set()

        def walk(n):
            if n.type == "call_expression":
                fn = n.child_by_field_name("function")
                if fn:
                    calls.add(self.node_text(code, fn))
            for c in n.children:
                walk(c)
        
        walk(node)
        return list(calls)
    
    def extract_functions(self, root_node, code):
        function_chunk = []
        imports = self.extract_imports(root_node, code)

        def walk(node):
            if node.type == "function_declaration":
                name_node = node.child_by_field_name("name")
                function_name = self.node_text(code, name_node) if name_node else "anonymous"

                params = []
                params_node = node.child_by_field_name("parameters")
                if params_node:
                    for p in params_node.children:
                        if p.type == "identifier":
                            params.append(self.node_text(code, p))

                function_chunk.append({
                    "type": "function",
                    "name": function_name,
                    "language": "javascript",
                    "imports": imports,
                    "params": params,
                    "code": self.node_text(code, name_node)
                })

            for child in node.children:
                walk(child)
        
        walk(root_node)
        return function_chunk
    
    def extract_arrow_functions(self, root_node, code):
        function_chunk = []
        imports = self.extract_imports(root_node, code)

        def walk(node):
            if node.type == "variable_declarator":
                name_node = node.child_by_field_name("name")
                value_node = node.child_by_field_name("value")

                if name_node and value_node and value_node.type == "arrow_function":
                    function_name = self.node_text(code, name_node)
                    params = []
                    params_node = value_node.child_by_field_name("parameters")
                    if params_node:
                        for p in params_node.children:
                            if p.type == "identifier":
                                params.append(self.node_text(code, p))
                
                    function_chunk.append({
                        "type": "arrow_function",
                        "name": function_name,
                        "language": "javascript",
                        "imports": imports,
                        "params": params,
                        "code": self.node_text(code, name_node)
                    })

            for child in node.children:
                walk(child)
        
        walk(root_node)
        return function_chunk
    
    def mutates_state(self, node, code):
        mutated = set()

        def walk(n):
            if n.type == "assignment_expression":
                left = n.child_by_field_name("left")
                if left and left.type == "member_expression":
                    if "this." in self.node_text(code, left):
                        mutated.add(self.node_text(code, left))
            for c in n.children:
                walk(c)
        
        walk(node)
        return mutated
    
    def extract_methods(self, class_node, code):
        methods = []

        for child in class_node.children:
            if child.type == "class_body":
                for member in child.children:
                    if member.type == "method_definition":
                        name_node = member.child_by_field_name("name")
                        name = self.node_text(code, name_node)

                        params_node = member.child_by_field_name("parameters")
                        params = []
                        if params_node:
                            for p in params_node.children:
                                if p.type == "identifier":
                                    params.append(self.node_text(code, p))

                        mutations = self.mutates_state(member, code)
                        methods.append({
                            "name": name,
                            "params": params,
                            "calls": self.extract_calls(member, code),
                            "mutatesState": bool(mutations),
                            "mutations": list(mutations),
                            "code": self.node_text(code, member)
                        })
        
        return methods
    
    def extract_classes(self, root_node, code):
        class_chunk = []
        imports = self.extract_imports(root_node, code)

        def walk(n):
            if n.type == "class_declaration":
                name_node = n.child_by_field_name("name")
                class_name = self.node_text(code, name_node)
                methods = self.extract_methods(n, code)

                class_chunk.append({
                    "type": "class",
                    "name": class_name,
                    "file_path": "file path",
                    "language": "javascript",
                    "imports": imports,
                    "constructor": "constructor",
                    "methods": methods,
                    "code": self.node_text(code, n)
                })
        
            for c in n.children:
                walk(c)
        
        walk(root_node)
        return class_chunk
    
    def extract_exports(self, root, code):
        exports = []

        def walk(node):
            # ES Modules
            if node.type == "export_statement":
                exports.append({
                    "type": "named_export",
                    "code": self.node_text(code, node)
                })

            if node.type == "export_default_declaration":
                exports.append({
                    "type": "default_export",
                    "code": self.node_text(code, node)
                })

            # CommonJS
            if node.type == "assignment_expression":
                left = node.child_by_field_name("left")
                if left and self.node_text(code, left).startswith(("module.exports", "exports.")):
                    exports.append({
                        "type": "commonjs_export",
                        "code": self.node_text(code, node)
                    })

            for child in node.children:
                walk(child)

        walk(root)
        return exports
    
    def analyze(self, code):
        root, code_bytes = self.parse(code)
        
        return {
            "imports": self.extract_imports(root, code_bytes),
            "functions": self.extract_functions(root, code_bytes),
            "arrow_functions": self.extract_arrow_functions(root, code_bytes),
            "classes": self.extract_classes(root, code_bytes),
            "exports": self.extract_exports(root, code_bytes)
        }

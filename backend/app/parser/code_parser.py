"""Tree-sitter based source code parser for repository files."""

from __future__ import annotations

import hashlib
from pathlib import Path

import structlog
from tree_sitter import Language, Node, Parser
import tree_sitter_javascript as ts_javascript
import tree_sitter_python as ts_python

from app.models.code_node import CodeNode

logger = structlog.get_logger(__name__)


class TreeSitterCodeParser:
    """Extract code entities and relationships from Python and JavaScript files."""

    SUPPORTED_EXTENSIONS = {".py", ".js", ".jsx", ".mjs", ".cjs"}

    def __init__(self) -> None:
        """Initialize Tree-sitter parsers by language."""
        self._parsers: dict[str, Parser] = {
            "python": self._build_parser(Language(ts_python.language())),
            "javascript": self._build_parser(Language(ts_javascript.language())),
        }

    def parse_repository(self, repo_path: Path, repo_name: str) -> list[CodeNode]:
        """Parse all supported source files from a repository."""
        nodes: list[CodeNode] = []
        for file_path in repo_path.rglob("*"):
            if not file_path.is_file() or file_path.suffix not in self.SUPPORTED_EXTENSIONS:
                continue
            relative_path = file_path.relative_to(repo_path)
            nodes.extend(self.parse_file(file_path, relative_path, repo_name))
        logger.info("repository_parsed", repo=repo_name, node_count=len(nodes))
        return nodes

    def parse_file(self, file_path: Path, relative_path: Path, repo_name: str) -> list[CodeNode]:
        """Parse a single file and return extracted function/class code nodes."""
        source = file_path.read_bytes()
        language_key = self._detect_language(file_path)
        parser = self._parsers[language_key]
        tree = parser.parse(source)

        imports = self._extract_imports(tree.root_node, source, language_key)
        extracted: list[CodeNode] = []
        self._walk_entities(
            tree.root_node,
            source=source,
            repo_name=repo_name,
            relative_path=relative_path,
            imports=imports,
            language_key=language_key,
            sink=extracted,
        )
        return extracted

    @staticmethod
    def _build_parser(language: Language) -> Parser:
        """Build a parser for a specific language."""
        parser = Parser(language)
        return parser

    @staticmethod
    def _detect_language(file_path: Path) -> str:
        """Map file extension to parser language key."""
        if file_path.suffix == ".py":
            return "python"
        return "javascript"

    def _walk_entities(
        self,
        node: Node,
        *,
        source: bytes,
        repo_name: str,
        relative_path: Path,
        imports: list[str],
        language_key: str,
        sink: list[CodeNode],
    ) -> None:
        """Recursively walk AST and collect function/class entities."""
        if self._is_entity(node, language_key):
            name = self._extract_entity_name(node, source, language_key)
            if name:
                body = source[node.start_byte : node.end_byte].decode("utf-8", errors="ignore")
                calls = self._extract_calls(node, source, language_key)
                node_type = "class" if "class" in node.type else "function"
                sink.append(
                    CodeNode(
                        id=self._build_node_id(repo_name, relative_path.as_posix(), node_type, name),
                        name=name,
                        type=node_type,
                        file_path=relative_path.as_posix(),
                        repo=repo_name,
                        calls=calls,
                        imports=imports,
                        content=body,
                    )
                )

        for child in node.children:
            self._walk_entities(
                child,
                source=source,
                repo_name=repo_name,
                relative_path=relative_path,
                imports=imports,
                language_key=language_key,
                sink=sink,
            )

    @staticmethod
    def _is_entity(node: Node, language_key: str) -> bool:
        """Check whether node is a supported code entity."""
        if language_key == "python":
            return node.type in {"function_definition", "class_definition"}
        return node.type in {"function_declaration", "method_definition", "class_declaration"}

    @staticmethod
    def _extract_entity_name(node: Node, source: bytes, language_key: str) -> str:
        """Extract class/function name from AST node."""
        if language_key == "python":
            name_node = node.child_by_field_name("name")
            if not name_node:
                return ""
            return source[name_node.start_byte : name_node.end_byte].decode("utf-8", errors="ignore")

        if node.type == "method_definition":
            name_node = node.child_by_field_name("name")
            if not name_node:
                return ""
            return source[name_node.start_byte : name_node.end_byte].decode("utf-8", errors="ignore")
        if node.type == "class_declaration":
            name_node = node.child_by_field_name("name")
            if not name_node:
                return ""
            return source[name_node.start_byte : name_node.end_byte].decode("utf-8", errors="ignore")
        if node.type == "function_declaration":
            name_node = node.child_by_field_name("name")
            if not name_node:
                return ""
            return source[name_node.start_byte : name_node.end_byte].decode("utf-8", errors="ignore")
        return ""

    @staticmethod
    def _extract_imports(root: Node, source: bytes, language_key: str) -> list[str]:
        """Extract import statements from full file AST."""
        imports: list[str] = []
        stack = [root]
        import_types = (
            {"import_statement", "import_from_statement"}
            if language_key == "python"
            else {"import_statement"}
        )
        while stack:
            node = stack.pop()
            if node.type in import_types:
                imports.append(source[node.start_byte : node.end_byte].decode("utf-8", errors="ignore").strip())
            stack.extend(node.children)
        return imports

    @staticmethod
    def _extract_calls(scope: Node, source: bytes, language_key: str) -> list[str]:
        """Extract method/function call names within an entity scope."""
        calls: list[str] = []
        stack = [scope]
        call_type = "call" if language_key == "python" else "call_expression"
        while stack:
            node = stack.pop()
            if node.type == call_type:
                target = node.child_by_field_name("function")
                if target is None and language_key == "javascript":
                    target = node.child_by_field_name("callee")
                if target is not None:
                    call_name = source[target.start_byte : target.end_byte].decode("utf-8", errors="ignore").strip()
                    if call_name:
                        calls.append(call_name)
            stack.extend(node.children)
        return calls

    @staticmethod
    def _build_node_id(repo: str, file_path: str, node_type: str, name: str) -> str:
        """Generate stable node id from deterministic string input."""
        raw = f"{repo}:{file_path}:{node_type}:{name}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


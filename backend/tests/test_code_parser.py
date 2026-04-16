"""Unit tests for Tree-sitter parser layer."""

from pathlib import Path

from app.parser.code_parser import TreeSitterCodeParser


def test_parse_python_file_extracts_functions_classes_calls_and_imports(tmp_path: Path) -> None:
    """Parser extracts expected entities from Python code."""
    code = """import os
from math import sqrt

class Service:
    def run(self):
        print("ok")

def helper():
    value = sqrt(4)
    return value
"""
    file_path = tmp_path / "sample.py"
    file_path.write_text(code, encoding="utf-8")

    parser = TreeSitterCodeParser()
    nodes = parser.parse_file(file_path, Path("sample.py"), "repo-a")

    names = {node.name for node in nodes}
    assert "Service" in names
    assert "run" in names
    assert "helper" in names
    helper = next(node for node in nodes if node.name == "helper")
    assert helper.type == "function"
    assert any("import os" in imp for imp in helper.imports)
    assert any("from math import sqrt" in imp for imp in helper.imports)
    assert "sqrt" in "".join(helper.calls)


def test_parse_javascript_file_extracts_entities(tmp_path: Path) -> None:
    """Parser extracts expected entities from JavaScript code."""
    code = """import axios from "axios";

class ApiClient {
  fetchData() {
    return axios.get("/x");
  }
}

function toUpper(value) {
  return value.toUpperCase();
}
"""
    file_path = tmp_path / "sample.js"
    file_path.write_text(code, encoding="utf-8")

    parser = TreeSitterCodeParser()
    nodes = parser.parse_file(file_path, Path("sample.js"), "repo-b")

    names = {node.name for node in nodes}
    assert "ApiClient" in names
    assert "fetchData" in names
    assert "toUpper" in names
    fetch = next(node for node in nodes if node.name == "fetchData")
    assert any("import axios" in imp for imp in fetch.imports)
    assert any("axios.get" in call for call in fetch.calls)


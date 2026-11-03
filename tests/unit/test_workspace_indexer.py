"""Unit test suite for IVA WorkspaceIndexer.
================================================================================
Tests:
1. Scanning directory, respecting ignore boundaries.
2. AST extraction of functions, classes, and method signatures.
3. Ingestion into mock memory adapter.
4. Recording indexed workspace metadata in registry.
================================================================================
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from agents.IVA.engine.agi17.memory.workspace_indexer import WorkspaceIndexer


class TestWorkspaceIndexer(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="iva_work_test_"))
        self.mock_memory = MagicMock()
        self.indexer = WorkspaceIndexer(memory_adapter=self.mock_memory)
        # Point registry file to temp
        self.indexer.registry_file = self.temp_dir / "indexed.json"

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_index_python_ast(self) -> None:
        sample_code = (
            "class DataProcessor:\n"
            "    def process(self, items, factor=1.0):\n"
            "        '''Processes items with factor.'''\n"
            "        return [i * factor for i in items]\n\n"
            "def standalone_func(val: int) -> int:\n"
            "    '''Doubles value.'''\n"
            "    return val * 2\n"
        )
        code_file = self.temp_dir / "processor.py"
        code_file.write_text(sample_code, encoding="utf-8")

        res = self.indexer.index_directory(self.temp_dir)
        self.assertEqual(res.total_files_scanned, 1)
        self.assertTrue(res.total_ast_nodes > 0)
        self.assertEqual(res.total_symbols_extracted, 3)

        sym_names = [s.name for s in res.symbols]
        self.assertIn("DataProcessor", sym_names)
        self.assertIn("process", sym_names)
        self.assertIn("standalone_func", sym_names)

        # Verify memory stored was called
        self.mock_memory.store.assert_called()

        # Check workspace metadata saved
        indexed = self.indexer.list_indexed_workspaces()
        self.assertEqual(len(indexed), 1)
        self.assertEqual(indexed[0]["total_files_scanned"], 1)

    def test_02_ignores_dot_dirs(self) -> None:
        git_dir = self.temp_dir / ".git"
        git_dir.mkdir()
        (git_dir / "config.py").write_text("def secret(): pass", encoding="utf-8")

        normal_file = self.temp_dir / "app.py"
        normal_file.write_text("def main(): pass", encoding="utf-8")

        res = self.indexer.index_directory(self.temp_dir)
        self.assertEqual(res.total_files_scanned, 1)
        self.assertEqual(res.symbols[0].name, "main")


if __name__ == "__main__":
    unittest.main()

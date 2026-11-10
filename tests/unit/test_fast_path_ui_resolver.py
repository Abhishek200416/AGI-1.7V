"""Unit tests for FastPathUIResolver."""

import os
import tempfile
import unittest
from pathlib import Path
from agents.IVA.engine.agi17.capabilities.fast_path_ui_resolver import FastPathUIResolver


class TestFastPathUIResolver(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name)
        self.db_path = self.workspace / "test_ui_memory.db"
        self.resolver = FastPathUIResolver(db_path=self.db_path)

        # Create mock HTML and CSS files
        self.html_file = self.workspace / "index.html"
        self.html_file.write_text("""
        <!DOCTYPE html>
        <html>
        <head><link rel="stylesheet" href="style.css"></head>
        <body>
            <header class="main-navbar">
                <nav><a href="#home">Home</a></nav>
            </header>
            <main>
                <div class="user-card" id="profile-card">
                    <h2>User Profile</h2>
                    <button id="submit-btn" class="primary-btn submit-action">Save Changes</button>
                </div>
                <div id="settings-modal" class="modal-sheet hidden">
                    <p>Settings Content</p>
                </div>
            </main>
        </body>
        </html>
        """, encoding="utf-8")

        self.css_file = self.workspace / "style.css"
        self.css_file.write_text("""
        .primary-btn {
            background-color: blue;
            color: white;
            padding: 10px 20px;
        }
        .main-navbar {
            padding: 15px;
            position: sticky;
        }
        """, encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_index_workspace_and_resolve_button(self):
        count = self.resolver.index_workspace(self.workspace)
        self.assertGreater(count, 0)

        # Intent: change submit button
        matches = self.resolver.resolve_intent(self.workspace, "change submit button color")
        self.assertGreater(len(matches), 0)
        top_match = matches[0]
        self.assertIn("submit-btn", top_match["identifier"])
        self.assertEqual(top_match["file_rel_path"], "index.html")

    def test_resolve_navbar_css(self):
        self.resolver.index_workspace(self.workspace)
        matches = self.resolver.resolve_intent(self.workspace, "fix main-navbar padding")
        self.assertGreater(len(matches), 0)
        # Should match style.css or index.html navbar
        rel_paths = [m["file_rel_path"] for m in matches]
        self.assertTrue("style.css" in rel_paths or "index.html" in rel_paths)

    def test_apply_surgical_patch(self):
        self.resolver.index_workspace(self.workspace)
        success = self.resolver.apply_surgical_patch(
            self.html_file,
            "Save Changes",
            "Update Profile",
        )
        self.assertTrue(success)
        content = self.html_file.read_text(encoding="utf-8")
        self.assertIn("Update Profile", content)
        self.assertNotIn("Save Changes", content)


if __name__ == "__main__":
    unittest.main()

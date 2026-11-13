import unittest
from agents.IVA.ecosystem.iva_skills_registry import (
    AivaSkillsCatalog,
    IvaSkillsRegistry,
    SkillCategory,
    iva_skills_registry,
)


class TestIvaSkillsRegistry(unittest.TestCase):
    def test_registry_initialization_and_alias(self):
        self.assertGreaterEqual(iva_skills_registry.total_count(), 35)
        self.assertEqual(len(iva_skills_registry.list_categories()), 10)
        # Test alias
        alias_instance = AivaSkillsCatalog()
        self.assertEqual(alias_instance.total_count(), iva_skills_registry.total_count())

    def test_all_10_categories_populated(self):
        for cat in SkillCategory:
            skills = iva_skills_registry.get_skills_by_category(cat)
            self.assertGreater(len(skills), 0, f"Category {cat.value} should have at least 1 skill")

    def test_skill_lookup_and_mcp_unification(self):
        # Look up an MCP server unified as a skill
        playwright_skill = iva_skills_registry.get_skill("playwright")
        self.assertIsNotNone(playwright_skill)
        self.assertEqual(playwright_skill.category, SkillCategory.BROWSER_AUTOMATION)
        self.assertIn("browser_navigate", playwright_skill.tools_or_commands)

        # Look up sequential-thinking
        seq_skill = iva_skills_registry.get_skill("sequential-thinking")
        self.assertIsNotNone(seq_skill)
        self.assertEqual(seq_skill.category, SkillCategory.CORE_INTELLIGENCE)

        # Look up Instagram & Omnichannel media skills
        ig_skill = iva_skills_registry.get_skill("iva-instagram-skill")
        self.assertIsNotNone(ig_skill)
        self.assertEqual(ig_skill.category, SkillCategory.MEDIA_STUDIO)

    def test_search_skills(self):
        results = iva_skills_registry.search_skills("quant")
        self.assertGreater(len(results), 0)
        found_names = [s.name for s in results]
        self.assertIn("omega-quant-trading", found_names)

    def test_unified_summary_structure(self):
        summary = iva_skills_registry.get_unified_summary()
        self.assertEqual(summary["total_categories_count"], 10)
        self.assertIn(SkillCategory.MEDIA_STUDIO.value, summary["categories"])

    def test_markdown_catalog_generation(self):
        md = iva_skills_registry.generate_markdown_catalog()
        self.assertIn("# IVA Skills Master Catalog (AIVA Skills)", md)
        self.assertIn("## Media Studio, Video Directing & Omnichannel Social", md)
        self.assertIn("`playwright`", md)


if __name__ == "__main__":
    unittest.main()

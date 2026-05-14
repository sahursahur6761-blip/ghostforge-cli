import unittest
import os
import json
import ghostforge

class TestGhostForge(unittest.TestCase):
    def setUp(self):
        # Create a temporary vault for testing
        self.test_vault_file = 'test_vault.json'
        ghostforge.VAULT_FILE = self.test_vault_file
        self.default_vault = {
            "player": {"level": 1, "xp": 0, "gold": 0, "class": "Novice", "inventory": []},
            "missions": [],
            "bosses": [],
            "history": []
        }
        with open(self.test_vault_file, 'w') as f:
            json.dump(self.default_vault, f)

    def tearDown(self):
        if os.path.exists(self.test_vault_file):
            os.remove(self.test_vault_file)

    def test_load_vault(self):
        vault = ghostforge.load_vault()
        self.assertEqual(vault['player']['level'], 1)

    def test_add_xp_and_level_up(self):
        vault = self.default_vault
        ghostforge.add_xp(vault, 150)
        self.assertEqual(vault['player']['level'], 2)
        self.assertEqual(vault['player']['xp'], 50)

    def test_promotion(self):
        vault = self.default_vault
        # Level 5 needed for promotion
        ghostforge.add_xp(vault, 1000) # Lvl 1->2 (100), 2->3 (200), 3->4 (300), 4->5 (400)
        self.assertEqual(vault['player']['level'], 5)
        self.assertEqual(vault['player']['class'], "Apprentice Coder")

    def test_boss_loot(self):
        vault = self.default_vault
        ghostforge.cmd_boss_spawn(vault, "Dragon", "Big bad", 100)
        ghostforge.cmd_boss_slay(vault, 0)
        self.assertIn("Artifact of Dragon", vault['player']['inventory'])

if __name__ == '__main__':
    unittest.main()

import unittest
import os
import json
import ghostforge
from datetime import datetime

class TestGhostForgeV3(unittest.TestCase):
    def setUp(self):
        self.test_vault_file = 'test_vault.json'
        ghostforge.VAULT_FILE = self.test_vault_file
        # Mocking the path
        ghostforge.get_vault_path = lambda: self.test_vault_file

        self.default_vault = {
            "player": {
                "level": 1, "xp": 0, "gold": 0, "sp": 0,
                "class": "Novice", "inventory": [], "titles": ["The Unforged"],
                "skills": {"efficiency": 0, "greed": 0, "luck": 0}
            },
            "missions": [], "bosses": [], "history": [], "shop": []
        }
        with open(self.test_vault_file, 'w') as f:
            json.dump(self.default_vault, f)

    def tearDown(self):
        if os.path.exists(self.test_vault_file):
            os.remove(self.test_vault_file)

    def test_sp_gain_on_level_up(self):
        vault = self.default_vault
        ghostforge.add_xp(vault, 150)
        self.assertEqual(vault['player']['level'], 2)
        self.assertEqual(vault['player']['sp'], 1)

    def test_efficiency_skill(self):
        vault = self.default_vault
        vault['player']['skills']['efficiency'] = 2 # +10% XP
        vault['player']['xp'] = 0
        ghostforge.add_xp(vault, 100)
        # 100 + 10% bonus = 110. But we were lvl 1 (100 xp needed), so it should level up and leave 10 XP.
        self.assertEqual(vault['player']['level'], 2)
        self.assertEqual(vault['player']['xp'], 10)

if __name__ == '__main__':
    unittest.main()

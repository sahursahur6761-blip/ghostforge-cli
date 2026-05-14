import unittest
import os
import json
import ghostforge
from datetime import datetime

class TestGhostForgeV2(unittest.TestCase):
    def setUp(self):
        self.test_vault_file = 'test_vault.json'
        ghostforge.VAULT_FILE = self.test_vault_file
        # Mocking the path for the tool's utility function if it uses it
        if hasattr(ghostforge, 'get_vault_path'):
             ghostforge.get_vault_path = lambda: self.test_vault_file

        self.default_vault = {
            "player": {"level": 1, "xp": 0, "gold": 0, "class": "Novice", "inventory": [], "titles": ["The Unforged"]},
            "missions": [],
            "bosses": [],
            "history": [],
            "shop": [{"name": "Test Item", "price": 10, "effect": "Test"}]
        }
        with open(self.test_vault_file, 'w') as f:
            json.dump(self.default_vault, f)

    def tearDown(self):
        if os.path.exists(self.test_vault_file):
            os.remove(self.test_vault_file)

    def test_economy_and_shop(self):
        vault = self.default_vault
        vault['player']['gold'] = 20
        ghostforge.cmd_shop(vault, 'buy', 0)
        self.assertEqual(vault['player']['gold'], 10)
        self.assertIn("Test Item", vault['player']['inventory'])

    def test_mission_gold_reward(self):
        vault = self.default_vault
        vault['missions'].append({"title": "Gold Rush", "reward": 100, "completed": False})
        ghostforge.cmd_mission_complete(vault, 0)
        self.assertEqual(vault['player']['gold'], 50) # 100 // 2

    def test_project_pulse_logging(self):
        vault = self.default_vault
        ghostforge.log_history(vault, "Test Event")
        self.assertEqual(len(vault['history']), 1)
        self.assertIn("timestamp", vault['history'][0])

if __name__ == '__main__':
    unittest.main()

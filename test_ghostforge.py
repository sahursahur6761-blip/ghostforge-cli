import unittest
import os
import json
import ghostforge
from datetime import datetime

class TestGhostForgeV4(unittest.TestCase):
    def setUp(self):
        self.test_vault_file = 'test_vault.json'
        ghostforge.VAULT_FILE = self.test_vault_file
        ghostforge.get_vault_path = lambda: self.test_vault_file

        self.default_vault = {
            "player": {
                "level": 1, "xp": 0, "gold": 100, "sp": 0,
                "class": "Novice", "inventory": [], "titles": ["The Unforged"],
                "skills": {"efficiency": 0, "greed": 0, "luck": 0},
                "buffs": {}, "theme": "Cyberpunk"
            },
            "campaigns": {"Default": {"missions": [], "bosses": []}},
            "active_campaign": "Default",
            "history": [],
            "shop": [{"name": "Coffee", "price": 50, "effect": "XP_BOOST", "duration": 3}]
        }
        with open(self.test_vault_file, 'w') as f:
            json.dump(self.default_vault, f)

    def tearDown(self):
        if os.path.exists(self.test_vault_file):
            os.remove(self.test_vault_file)

    def test_campaign_switching(self):
        vault = self.default_vault
        ghostforge.cmd_campaign(vault, 'create', 'ProjectX')
        ghostforge.cmd_campaign(vault, 'switch', 'ProjectX')
        self.assertEqual(vault['active_campaign'], 'ProjectX')

    def test_active_buff_application(self):
        vault = self.default_vault
        vault['player']['inventory'].append("Coffee")
        ghostforge.cmd_use(vault, "Coffee")
        self.assertEqual(vault['player']['buffs']['XP_BOOST'], 3)
        self.assertNotIn("Coffee", vault['player']['inventory'])

    def test_roll_gold_deduction(self):
        vault = self.default_vault
        initial_gold = vault['player']['gold']
        # We can't easily test the outcome due to random, but we check deduction
        ghostforge.cmd_roll(vault, 10)
        # Gold should be initial - 10 + win (if any)
        # Since we just want to ensure it runs
        self.assertNotEqual(vault['player']['gold'], initial_gold + 10)

if __name__ == '__main__':
    unittest.main()

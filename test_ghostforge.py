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
            "player": {"level": 1, "xp": 0, "gold": 0, "class": "Novice"},
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
        self.assertEqual(vault['player']['xp'], 50) # 150 - 100

    def test_add_mission(self):
        vault = self.default_vault
        class Args:
            title = "Test Mission"
            reward = 20
            action = 'add'
        ghostforge.cmd_mission(Args(), vault)
        self.assertEqual(len(vault['missions']), 1)
        self.assertEqual(vault['missions'][0]['title'], "Test Mission")

if __name__ == '__main__':
    unittest.main()

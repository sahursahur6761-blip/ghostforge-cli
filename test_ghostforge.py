import unittest
import os
import json
import ghostforge
import shutil
from datetime import datetime

class TestGhostForgeV5(unittest.TestCase):
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
            "journal": [],
            "shop": []
        }
        with open(self.test_vault_file, 'w') as f:
            json.dump(self.default_vault, f)

    def tearDown(self):
        if os.path.exists(self.test_vault_file):
            os.remove(self.test_vault_file)
        if os.path.exists('.forge_backups'):
            shutil.rmtree('.forge_backups')

    def test_journal_entry(self):
        vault = self.default_vault
        ghostforge.cmd_journal(vault, 'add', "Test Log Entry")
        self.assertEqual(len(vault['journal']), 1)
        self.assertEqual(vault['journal'][0]['text'], "Test Log Entry")

    def test_mission_priority(self):
        vault = self.default_vault
        c = vault['campaigns']['Default']
        c['missions'].append({"title": "Critical", "reward": 50, "completed": False, "priority": "High"})
        self.assertEqual(c['missions'][0]['priority'], "High")

    def test_backup_creation(self):
        # We need a real file for backup to work as it uses shutil.copy2
        with open(ghostforge.VAULT_FILE, 'w') as f:
            json.dump(self.default_vault, f)
        ghostforge.cmd_backup(self.default_vault)
        self.assertTrue(os.path.exists('.forge_backups'))
        self.assertTrue(len(os.listdir('.forge_backups')) > 0)

if __name__ == '__main__':
    unittest.main()

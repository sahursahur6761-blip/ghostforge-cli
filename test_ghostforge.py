import unittest
import os
import json
import ghostforge
import shutil
from datetime import datetime

class TestGhostForgeV8(unittest.TestCase):
    def setUp(self):
        self.test_vault = os.path.expanduser('~/test_ghostforge_vault_v8.json')
        if os.path.exists(self.test_vault):
            os.remove(self.test_vault)
        self.forge = ghostforge.Forge(vault_path=self.test_vault)

    def tearDown(self):
        if os.path.exists(self.test_vault):
            os.remove(self.test_vault)

    def test_energy_initial_state(self):
        self.assertEqual(self.forge.p['energy'], 50)
        self.assertEqual(self.forge.p['max_energy'], 50)

    def test_netrunner_spec_xp_bonus(self):
        self.forge.p['spec'] = 'Netrunner'
        # Base XP 100 + 20% Netrunner bonus = 120
        self.forge.add_xp(100)
        # Lvl 1->2 takes 100. 120 total leaves 20 XP at Lvl 2.
        self.assertEqual(self.forge.p['level'], 2)
        self.assertEqual(self.forge.p['xp'], 20)

    def test_auto_backup_logic(self):
        # Initial backup on init should set last_backup
        self.assertIsNotNone(self.forge.vault.get('last_backup'))

if __name__ == '__main__':
    unittest.main()

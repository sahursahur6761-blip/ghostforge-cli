import unittest
import os
import json
import ghostforge
import shutil
from datetime import datetime

class TestGhostForgeV7(unittest.TestCase):
    def setUp(self):
        # Use a temporary vault for testing to avoid touching user's ~/.vault
        self.test_vault = os.path.expanduser('~/test_ghostforge_vault_v7.json')
        if os.path.exists(self.test_vault):
            os.remove(self.test_vault)
        self.forge = ghostforge.Forge(vault_path=self.test_vault)

    def tearDown(self):
        if os.path.exists(self.test_vault):
            os.remove(self.test_vault)

    def test_equipment_bonus(self):
        # Initial ATK is 10
        initial_atk = self.forge.p['atk']
        # Cyberdeck is ID 0 in shop, +15 ATK
        self.forge.p['gold'] = 1000
        self.forge.cmd_shop('buy', 0)
        self.assertEqual(self.forge.p['atk'], initial_atk + 15)

    def test_xp_and_level_up(self):
        initial_level = self.forge.p['level']
        # Level 1 -> 2 takes 100 XP
        self.forge.add_xp(150)
        self.assertEqual(self.forge.p['level'], 2)
        self.assertEqual(self.forge.p['xp'], 50)
        self.assertEqual(self.forge.p['max_hp'], 120) # 100 + 20

    def test_boss_spawn(self):
        c = self.forge.vault['campaigns']['Default']
        initial_count = len(c['bosses'])
        c['bosses'].append({"name": "Test Boss", "defeated": False})
        self.assertEqual(len(c['bosses']), initial_count + 1)

if __name__ == '__main__':
    unittest.main()

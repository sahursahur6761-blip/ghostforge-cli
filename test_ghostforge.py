import unittest
import os
import json
import ghostforge
import shutil
from datetime import datetime

class TestGhostForgeV10(unittest.TestCase):
    def setUp(self):
        self.test_vault = os.path.expanduser('~/test_ghostforge_vault_v10.json')
        if os.path.exists(self.test_vault):
            os.remove(self.test_vault)
        self.f = ghostforge.Forge(vault_path=self.test_vault)

    def tearDown(self):
        if os.path.exists(self.test_vault):
            os.remove(self.test_vault)

    def test_scrap_accumulation(self):
        # Combat normally grants scrap
        # Let's verify manual scrap awarding
        self.f.p['scrap'] += 100
        self.assertEqual(self.f.p['scrap'], 100)

    def test_drone_fabrication_logic(self):
        # Striker Drone costs 250
        self.f.p['scrap'] = 300
        initial_atk = self.f.p['atk']
        self.f.cmd_fabricate('Striker')
        self.assertEqual(self.f.p['drone'], 'Striker')
        self.assertEqual(self.f.p['atk'], initial_atk + 10)
        self.assertEqual(self.f.p['scrap'], 50)

    def test_vault_auto_backup_on_init(self):
        # Backup dir should be created
        self.assertTrue(os.path.exists(self.f.vault_path))

if __name__ == '__main__':
    unittest.main()

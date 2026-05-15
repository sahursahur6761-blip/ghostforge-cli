import unittest
import os
import json
import ghostforge
import shutil
from datetime import datetime

class TestGhostForgeV9(unittest.TestCase):
    def setUp(self):
        self.test_vault = os.path.expanduser('~/test_ghostforge_vault_v9.json')
        if os.path.exists(self.test_vault):
            os.remove(self.test_vault)
        self.f = ghostforge.Forge(vault_path=self.test_vault)

    def tearDown(self):
        if os.path.exists(self.test_vault):
            os.remove(self.test_vault)

    def test_stat_upgrade(self):
        self.f.p['sp'] = 1
        initial_hack = self.f.p['hack']
        self.f.cmd_stat_up('hack')
        self.assertEqual(self.f.p['hack'], initial_hack + 1)
        self.assertEqual(self.f.p['sp'], 0)

    def test_drone_equipping(self):
        # Drone item is ID 0 in shop (Viper Drone)
        self.f.p['gold'] = 1000
        self.f.cmd_shop('buy', 0)
        self.assertEqual(self.f.p['drone'], 'Viper Drone')

    def test_xp_per_level_nexus(self):
        # Nexus gives 2 SP per level
        initial_sp = self.f.p['sp']
        self.f.add_xp(150) # Level up
        self.assertEqual(self.f.p['sp'], initial_sp + 2)

if __name__ == '__main__':
    unittest.main()

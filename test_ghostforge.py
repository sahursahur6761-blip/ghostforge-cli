import unittest
import os
import json
import ghostforge
import shutil
from datetime import datetime

class TestGhostForgeV6(unittest.TestCase):
    def setUp(self):
        self.test_vault_file = 'test_vault.json'
        if os.path.exists(self.test_vault_file):
            os.remove(self.test_vault_file)
        self.forge = ghostforge.Forge(vault_path=self.test_vault_file)

    def tearDown(self):
        if os.path.exists(self.test_vault_file):
            os.remove(self.test_vault_file)
        if os.path.exists('.forge_backups'):
            shutil.rmtree('.forge_backups')

    def test_research_logic_multiplier(self):
        self.forge.p['research']['logic'] = 1
        self.forge.p['xp'] = 0
        self.forge.add_xp(100)
        self.assertEqual(self.forge.p['level'], 2)
        self.assertEqual(self.forge.p['xp'], 10)

    def test_shard_multiplier(self):
        self.forge.p['shards'] = 1
        self.forge.p['xp'] = 0
        self.forge.add_xp(150)
        self.assertEqual(self.forge.p['level'], 3)
        self.assertEqual(self.forge.p['xp'], 0)

    def test_atomic_save(self):
        self.forge.p['gold'] = 999
        self.forge.save()
        with open(self.test_vault_file, 'r') as f:
            v = json.load(f)
            self.assertEqual(v['player']['gold'], 999)

    def test_journal_add(self):
        self.forge.cmd_journal('add', "Entry 1")
        self.assertEqual(len(self.forge.vault['journal']), 1)
        self.assertEqual(self.forge.vault['journal'][0]['text'], "Entry 1")

if __name__ == '__main__':
    unittest.main()

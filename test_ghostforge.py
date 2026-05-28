import unittest
import os
import json
import ghostforge
import shutil
from datetime import datetime

class TestGhostForgeV11(unittest.TestCase):
    def setUp(self):
        self.test_vault = os.path.expanduser('~/test_ghostforge_vault_v11.json')
        if os.path.exists(self.test_vault):
            os.remove(self.test_vault)
        # Point the forge class to our test vault
        self.f = ghostforge.Forge(vault_path=self.test_vault)

    def tearDown(self):
        if os.path.exists(self.test_vault):
            os.remove(self.test_vault)

    def test_persona_initialization(self):
        self.assertIn(self.f.persona, ['Aggressive', 'Cynical', 'Helpful'])

    def test_neural_link_update(self):
        # Trigger an event that saves
        self.f.vault['history'].append({"event": "Testing Link"})
        self.f.save()

        shared_file = '/tmp/.ghostforge_neural_link.json'
        self.assertTrue(os.path.exists(shared_file))
        with open(shared_file, 'r') as f:
            data = json.load(f)

        user_name = self.f.p['name']
        self.assertIn(user_name, data)
        self.assertEqual(data[user_name]['deed'], "Testing Link")

if __name__ == '__main__':
    unittest.main()

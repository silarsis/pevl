import unittest
import event

class TestEventWrapper(unittest.TestCase):
    def test_default_version(self):
        e = event.Event({'test': 'one', 'version': '0.1'})
        self.assertEqual(e.version, '0.1')

    def test_custom_version(self):
        e = event.Event({'test': 'one', 'version': '0.1'}, get_version=lambda x: '0.2')
        self.assertEqual(e.version, '0.2')

    def test_single_upgrade_mutation(self):
        @event.upgrade('0.1')
        def set_name(event):
            event['name'] = 'test_single_upgrade_mutation'
            event['version'] = '0.2'
        e = event.Event({'test': 'one', 'version': '0.1'})
        upgraded = set_name(e)
        self.assertEqual(upgraded.event['name'], 'test_single_upgrade_mutation')

    def test_single_upgrade_return(self):
        @event.upgrade('0.1')
        def set_name(event):
            event['name'] = 'test_single_upgrade_mutation'  # This should be overridden by the returned value
            return {'totally': 'different', 'dict': 'test'}
        e = event.Event({'test': 'one', 'version': '0.1'})
        upgraded = set_name(e)
        self.assertEqual(upgraded.event['totally'], 'different')

    def test_unmatched_version(self):
        @event.upgrade('0.2')
        def set_name(event):
            event['name'] = 'test_unmatched_version'
        e = event.Event({'test': 'one', 'version': '0.1'})
        upgraded = set_name(e)
        with self.assertRaises(KeyError):
            upgraded.event['name']

    def test_unmutated_event(self):
        @event.upgrade('0.1')
        def set_name(event):
            event['name'] = 'test_single_upgrade_mutation'
            event['version'] = '0.2'
        e = event.Event({'test': 'one', 'version': '0.1'})
        upgraded = set_name(e)
        with self.assertRaises(KeyError):
            e.event['name']

    def test_implicit_version_upgrade(self):
        @event.upgrade('0.1', '0.2')
        def set_name(event):
            event['name'] = 'test_single_upgrade_mutation'
        e = event.Event({'test': 'one', 'version': '0.1'})
        upgraded = set_name(e)
        self.assertEqual(upgraded.event['version'], '0.2')
        self.assertEqual(upgraded.version, '0.2')

    def test_version_not_upgraded(self):
        @event.upgrade('0.1')
        def set_name(event):
            event['name'] = 'test_single_upgrade_mutation'
        e = event.Event({'test': 'one', 'version': '0.1'})
        with self.assertRaises(KeyError):
            upgraded = set_name(e)

        
if __name__ == '__main__':
    unittest.main()
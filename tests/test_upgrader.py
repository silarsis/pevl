import unittest
import event

class TestUpgrader(unittest.TestCase):
    def test_multiple_versions(self):
        @event.upgrade('0.1', '0.2')
        def set_name(event):
            event['name'] = 'first upgrade'
        @event.upgrade('0.2', '0.3')
        def reset_name(event):
            event['name'] = 'second upgrade'
        upgrader = event.Upgrader([set_name, reset_name])
        e = {'test': 'one', 'version': '0.1'}
        u = upgrader.upgrade(e)
        self.assertEqual(u['name'], 'second upgrade')
        self.assertEqual(u['version'], '0.3')

    def test_exception_if_not_upgraded(self):
        @event.upgrade('0.1')
        def set_name(event):
            event['name'] = 'first upgrade'
        upgrader = event.Upgrader([set_name])
        e = {'test': 'one', 'version': '0.1'}
        with self.assertRaises(KeyError):
            u = upgrader.upgrade(e)

    def test_no_version(self):
        @event.upgrade('0.1', '0.2')
        def set_name(event):
            event['name'] = 'test_single_upgrade_mutation'
        upgrader = event.Upgrader([set_name])
        e = {'test': 'one'}
        u = upgrader.upgrade(e)
        self.assertEqual(u['test'], 'one')
        self.assertFalse('version' in u)
        self.assertFalse('name' in u)

    def test_target_version_failure(self):
        @event.upgrade('0.1', '0.2')
        def set_name(event):
            event['name'] = 'test_single_upgrade_mutation'
        upgrader = event.Upgrader([set_name])
        e = {'test': 'one', 'version': '0.1'}
        with self.assertRaises(KeyError):
            u = upgrader.upgrade(e, target_version='0.3')

    def test_target_version_break(self):
        @event.upgrade('0.1', '0.2')
        def set_name(event):
            event['name'] = 'first upgrade'
        @event.upgrade('0.2', '0.3')
        def reset_name(event):
            event['name'] = 'second upgrade'
        upgrader = event.Upgrader([set_name, reset_name])
        e = {'test': 'one', 'version': '0.1'}
        u = upgrader.upgrade(e, target_version='0.2')
        self.assertEqual(u['name'], 'first upgrade')
        self.assertEqual(u['version'], '0.2')

    def test_ingest_factory(self):
        @event.upgrade('0.1', '0.2')
        def set_name(event: dict):
            event['name'] = 'first upgrade'
        @event.upgrade('0.2', '0.3')
        def reset_name(event: dict):
            event['name'] = 'second upgrade'
        def factory(event: dict):
            return 'factory for {test} {name}'.format(**event)
        upgrader = event.Upgrader([set_name, reset_name], factory=factory)
        e = {'test': 'one', 'version': '0.1'}
        u = upgrader.ingest(e, target_version='0.3')
        self.assertEqual(u, 'factory for one second upgrade')
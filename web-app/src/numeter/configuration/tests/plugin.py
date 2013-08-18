from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from core.models import Host
from core.tests.utils import storage_enabled, set_storage
from multiviews.models import Plugin, Data_Source


class Plugin_TestCase(TestCase):
    fixtures = ['test_users.json','test_storage.json']

    @set_storage()
    def setUp(self):
        self.c = Client()
        self.c.login(username='root', password='toto')
        self.storage._update_hosts()
        if not Host.objects.exists():
            self.skipTest("There's no host in storage.")
        self.host = Host.objects.all()[0]

    def tearDown(self):
        Host.objects.all().delete()
        Plugin.objects.all().delete()
        Data_Source.objects.all().delete()

    def test_index(self):
        """Get plugin index."""
        url = reverse('plugin index')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_plugin_list(self):
        """Get plugin list."""
        url = reverse('plugin list')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_create_plugin_from_host(self):
        """Create plugin from host ids."""
        # Test GET
        url = reverse('plugin create')
        GET = {'host_id':self.host.id}
        r = self.c.get(url, GET)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        plugins = [ p['Plugin'] for p in self.host.get_plugins() ]
        chosen_plugins = plugins[:1]
        POST = {'host_id':self.host.id, 'plugins[]':chosen_plugins}
        r = self.c.post(url, POST)
        # Test if plugins have been created
        saved_plugins = Plugin.objects.all()
        self.assertTrue(saved_plugins.exists(), "No plugin have been created.")

        # Test to create false plugin
        POST = {'host_id':self.host.id, 'plugins[]':['FALSE']}
        r = self.c.post(url, POST)
        saved_plugins = Plugin.objects.all()
        self.assertEqual(saved_plugins.count(), 1, "False plugins can be created.")

        # Test to recreate a plugin
        POST = {'host_id':self.host.id, 'plugins[]':chosen_plugins}
        r = self.c.post(url, POST)
        saved_plugins = Plugin.objects.all()
        self.assertEqual(saved_plugins.count(), 1, "Can create duplicate plugin.")

    def test_get(self):
        """Get a plugin."""
        plugin = Plugin.objects.create_from_host(self.host)[0]
        url = reverse('plugin', args=[1])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_create_sources(self):
        """Create sources from a plugin."""
        plugin = Plugin.objects.create_from_host(self.host)[0]
        # Test GET
        url = reverse('plugin create sources', args=[plugin.id])
        GET = {'host_id':self.host.id}
        r = self.c.get(url, GET)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        sources = plugin.get_data_sources()
        chosen_sources = sources[:1]
        POST = {'host_id':self.host.id, 'sources[]':chosen_sources}
        r = self.c.post(url, POST)
        # Test if sources have been created
        sources = Data_Source.objects.all()
        self.assertTrue(sources.exists(), "No source have been created.")

    def test_update(self):
        """
        Simulate a POST which change a plugin.
        Test to see if comment has changed.
        """
        # Test to update
        plugins = Plugin.objects.create_from_host(self.host)
        plugin = Plugin.objects.get(pk=1)
        url = reverse('plugin update', args=[1])
        POST = { 'comment': 'test comment' }
        r = self.c.post(url, POST) 
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test if updated
        plugin = Plugin.objects.get(pk=1)
        self.assertEqual(plugin.comment, 'test comment', 'Comment is not changed (%s).' % plugin.comment)

    def test_delete(self):
        """
        Test to delete plugin and if can't get it.
        """
        plugin = Plugin.objects.create_from_host(self.host)[0]
        # Test to delete
        url = reverse('plugin delete', args=[plugin.id])
        r = self.c.post(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test to get it
        url = reverse('plugin', args=[plugin.id])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 404, "Bad response code (%i)." % r.status_code)



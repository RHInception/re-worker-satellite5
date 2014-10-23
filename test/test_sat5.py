# Copyright (C) 2014 SEE AUTHORS FILE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Unittests.
"""

import xmlrpclib
import mock

from . import TestCase
from contextlib import nested

from replugin import satellite5worker

MQ_CONF = {
    'server': '127.0.0.1',
    'port': 5672,
    'vhost': '/',
    'user': 'guest',
    'password': 'guest',
}


class TestSat5Worker(TestCase):
    def setUp(self):
        """Set up some reusable mocks and vars"""
        self.config_good = {
            "queue": "satellite5",
            "satellite_url": "https://satellite.example.com/rpc/api",
            "satellite_login": "username",
            "satellite_password": "password"
        }

        self.config_bad = {
            "queue": "satellite5"
        }

        self.config_bad_url = {
            "satellite_url": "httpderp://satellite.example.com/rpc/api",
            "satellite_login": "username",
            "satellite_password": "password"
        }

        self.config_auth_bad = {
            "satellite_url": "https://satellite.example.com/rpc/api",
            "satellite_login": "usernamebad",
            "satellite_password": "passwordbad"
        }

        # Misc MQ Stuff
        self.channel = mock.MagicMock('pika.spec.Channel')

        self.channel.basic_consume = mock.Mock('basic_consume')
        self.channel.basic_ack = mock.Mock('basic_ack')
        self.channel.basic_publish = mock.Mock('basic_publish')

        self.basic_deliver = mock.MagicMock()
        self.basic_deliver.delivery_tag = 123

        self.properties = mock.MagicMock(
            'pika.spec.BasicProperties',
            correlation_id=123,
            reply_to='me')

        self.logger = mock.MagicMock('logging.Logger').__call__()
        self.app_logger = mock.MagicMock('logging.Logger').__call__()
        self.connection = mock.MagicMock('pika.SelectConnection')

    def tearDown(self):
        """
        After every test.
        """
        TestCase.tearDown(self)
        self.channel.reset_mock()
        self.channel.basic_consume.reset_mock()
        self.channel.basic_ack.reset_mock()
        self.channel.basic_publish.reset_mock()

        self.basic_deliver.reset_mock()
        self.properties.reset_mock()

        self.logger.reset_mock()
        self.app_logger.reset_mock()
        self.connection.reset_mock()

    def test_verify_satellite_config_good(self):
        """We can identify a valid config file"""
        with nested(
                mock.patch('pika.SelectConnection'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.notify'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.send')):

            worker = satellite5worker.Satellite5Worker(
                MQ_CONF,
                logger=self.app_logger)
            worker._on_open(self.connection)
            worker._on_channel_open(self.channel)

            config_good = worker.verify_config(self.config_good)
            self.assertTrue(config_good)

    def test_verify_satellite_config_bad(self):
        """We can identify an invalid config file"""
        with nested(
                mock.patch('pika.SelectConnection'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.notify'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.send')):

            worker = satellite5worker.Satellite5Worker(
                MQ_CONF,
                logger=self.app_logger)
            worker._on_open(self.connection)
            worker._on_channel_open(self.channel)

            config_bad = worker.verify_config(self.config_bad)
            self.assertFalse(config_bad)

            config_bad_url = worker.verify_config(self.config_bad_url)
            self.assertFalse(config_bad)

    def test_verify_subcommand_good(self):
        """Verify we can detect good subcommands"""
        good_params = {
            'command': 'satellite5',
            'subcommand': 'Promote'
        }

        with nested(
                mock.patch('pika.SelectConnection'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.notify'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.send')):

            worker = satellite5worker.Satellite5Worker(
                MQ_CONF,
                logger=self.app_logger)
            worker._on_open(self.connection)
            worker._on_channel_open(self.channel)

            result_good = worker.verify_subcommand(good_params)
            self.assertTrue(result_good)

    def test_verify_subcommand_bad(self):
        """Verify we can detect bad subcommands"""
        bad_params = {
            'command': 'satellite5',
            'subcommand': 'Demote'
        }

        with nested(
                mock.patch('pika.SelectConnection'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.notify'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.send')):

            worker = satellite5worker.Satellite5Worker(
                MQ_CONF,
                logger=self.app_logger)
            worker._on_open(self.connection)
            worker._on_channel_open(self.channel)

            with self.assertRaises(satellite5worker.Satellite5WorkerError):
                result_bad = worker.verify_subcommand(bad_params)

    def test_verify_subcommand_parameters_good(self):
        """We are able to identify correct parameters"""
        good_dynamic_params = {
            'promote_from_label': 'test01',
            'promote_to_label': 'test02'
        }

        with nested(
                mock.patch('pika.SelectConnection'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.notify'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.send')):

            worker = satellite5worker.Satellite5Worker(
                MQ_CONF,
                logger=self.app_logger)
            worker._on_open(self.connection)
            worker._on_channel_open(self.channel)

            result_good = worker.verify_Promote_params(good_dynamic_params)
            self.assertTrue(result_good)

    def test_verify_subcommand_parameters_bad(self):
        """We are able to identify incorrect parameters"""
        bad_dynamic_params = {
            'badkey': 'herp',
            'badderkey': 'derp'
        }

        with nested(
                mock.patch('pika.SelectConnection'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.notify'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.send')):

            worker = satellite5worker.Satellite5Worker(
                MQ_CONF,
                logger=self.app_logger)
            worker._on_open(self.connection)
            worker._on_channel_open(self.channel)

            with self.assertRaises(satellite5worker.Satellite5WorkerError):
                result_bad = worker.verify_Promote_params(bad_dynamic_params)

    @mock.patch('replugin.satellite5worker.xmlrpclib.Server')
    def test_open_client_good(self, xmlserver):
        """Opening a connection returns a Server Proxy and auth key"""
        session_string = "sessionKeyString"
        # client.auth
        auth = mock.MagicMock()
        # client.auth.login
        login = mock.Mock(return_value=session_string)
        auth.login = login

        # client = xmlrpclib.Server()
        client = mock.MagicMock()
        client.auth = auth

        # xmlrpclib.Server()
        xmlserver.return_value = client

        with nested(
                mock.patch('pika.SelectConnection'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.notify'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.send')):

            worker = satellite5worker.Satellite5Worker(
                MQ_CONF,
                logger=self.app_logger)
            worker._on_open(self.connection)
            worker._on_channel_open(self.channel)

            (client, key) = worker.open_client(self.config_good)
            self.assertEqual(key, session_string)
            xmlserver.asser_called_once_with(self.config_good['satellite_url'])
            login.asser_called_once_with('username', 'password')

    @mock.patch('replugin.satellite5worker.xmlrpclib.Server')
    def test_open_client_bad(self, xmlserver):
        """Failing to connect raises an exception"""
        session_string = "sessionKeyString"
        # client.auth
        auth = mock.MagicMock()
        # client.auth.login
        login = mock.Mock(return_value=session_string)
        auth.login = login

        # client = xmlrpclib.Server()
        client = mock.MagicMock()
        client.auth = auth

        # xmlrpclib.Server()
        xmlserver.return_value = client

        with nested(
                mock.patch('pika.SelectConnection'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.notify'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.send')):

            worker = satellite5worker.Satellite5Worker(
                MQ_CONF,
                logger=self.app_logger)
            worker._on_open(self.connection)
            worker._on_channel_open(self.channel)

            # e.faultcode for auth fail = 2950
            client.auth.login.side_effect = [
                xmlrpclib.Fault(2950, "Authentication error"),
                xmlrpclib.Fault(1234, "Other error")
            ]
            with self.assertRaises(satellite5worker.Satellite5WorkerError):
                (client, key) = worker.open_client(self.config_auth_bad)

            with self.assertRaises(satellite5worker.Satellite5WorkerError):
                (client, key) = worker.open_client(self.config_auth_bad)

    def test_verify_Promote_channels_good(self):
        """We're able to find the source and destination channels"""
        key = "sessionKeyString"
        client = mock.MagicMock()

        # client.channel
        channel = mock.MagicMock()
        client.channel = channel

        # client.channel.software
        software = mock.MagicMock()
        channel.software = software

        # client.channel.software.getDetails()
        getDetails = mock.Mock(return_value={})
        software.getDetails = getDetails

        with nested(
                mock.patch('pika.SelectConnection'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.notify'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.send')):

            worker = satellite5worker.Satellite5Worker(
                MQ_CONF,
                logger=self.app_logger)
            worker._on_open(self.connection)
            worker._on_channel_open(self.channel)

            found_channels = worker.verify_Promote_channels(client, key,
                                                            'sourcechannel',
                                                            'destchannel')

            self.assertTrue(found_channels)

    def test_verify_source_channel_bad(self):
        """We notice when source/dest channels don't exist"""
        key = "sessionKeyString"
        client = mock.MagicMock()

        # client.channel
        channel = mock.MagicMock()
        client.channel = channel

        # client.channel.software
        software = mock.MagicMock()
        channel.software = software

        # client.channel.software.getDetails()
        getDetails = mock.Mock(return_value={})
        getDetails.side_effect = xmlrpclib.Fault(12345, 'Could not locate channel')
        software.getDetails = getDetails

        with nested(
                mock.patch('pika.SelectConnection'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.notify'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.send')):

            worker = satellite5worker.Satellite5Worker(
                MQ_CONF,
                logger=self.app_logger)
            worker._on_open(self.connection)
            worker._on_channel_open(self.channel)

            with self.assertRaises(satellite5worker.Satellite5WorkerError):
                found_channels = worker.verify_Promote_channels(client, key,
                                                                'sourcechannel',
                                                                'destchannel')

    def test_merge_packages_good(self):
        """We can merge channels properly"""
        key = "sessionKeyString"
        client = mock.MagicMock()
        example_package = {'package': 'name'}

        # client.channel
        channel = mock.MagicMock()
        client.channel = channel

        # client.channel.software
        software = mock.MagicMock()
        channel.software = software

        # client.channel.software.mergePackages()
        #
        # - mergePackages returns a list of dicts's, each dict is a
        # - package which was promoted
        mergePackages = mock.Mock(return_value=[example_package])
        software.mergePackages = mergePackages

        with nested(
                mock.patch('pika.SelectConnection'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.notify'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.send')):

            worker = satellite5worker.Satellite5Worker(
                MQ_CONF,
                logger=self.app_logger)
            worker._on_open(self.connection)
            worker._on_channel_open(self.channel)

            result = worker.do_Promote_channel_merge(client, key,
                                                     'sourcechannel', 'destchannel')
            # one package was 'promoted'
            self.assertEqual(result, 1)
            mergePackages.assert_called_once_with(key, 'sourcechannel', 'destchannel')

    def test_merge_packages_bad(self):
        """We notice when merging the channels fails"""
        key = "sessionKeyString"
        client = mock.MagicMock()

        # client.channel
        channel = mock.MagicMock()
        client.channel = channel

        # client.channel.software
        software = mock.MagicMock()
        channel.software = software

        # client.channel.software.mergePackages()
        #
        # - mergePackages returns a list of dicts's, each dict is a
        # - package which was promoted
        mergePackages = mock.Mock()
        mergePackages.side_effect = xmlrpclib.Fault(1234, 'Could not merge channels')
        software.mergePackages = mergePackages

        with nested(
                mock.patch('pika.SelectConnection'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.notify'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.send')):

            worker = satellite5worker.Satellite5Worker(
                MQ_CONF,
                logger=self.app_logger)
            worker._on_open(self.connection)
            worker._on_channel_open(self.channel)

            with self.assertRaises(satellite5worker.Satellite5WorkerError):
                result = worker.do_Promote_channel_merge(client, key,
                                                         'sourcechannel', 'destchannel')
                mergePackages.assert_called_once_with('sourcechannel', 'destchannel')

    def test_close_client_good(self):
        """We can successfully close the client connection"""
        session_string = "sessionKeyString"
        # client.auth
        auth = mock.MagicMock()
        # client.auth.login
        logout = mock.Mock(return_value=session_string)
        auth.logout = logout

        # client = xmlrpclib.Server()
        client = mock.MagicMock()
        client.auth = auth

        with nested(
                mock.patch('pika.SelectConnection'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.notify'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.send')):

            worker = satellite5worker.Satellite5Worker(
                MQ_CONF,
                logger=self.app_logger)
            worker._on_open(self.connection)
            worker._on_channel_open(self.channel)

            result = worker.close_client(client, session_string)
            self.assertTrue(result)
            logout.asser_called_once_with(session_string)

    def test_close_client_bad(self):
        """We notice if there's an issue closing the connection"""
        session_string = "sessionKeyString"
        # client.auth
        auth = mock.MagicMock()
        # client.auth.login
        logout = mock.Mock(return_value=session_string)
        logout.side_effect = Exception("HORRRRKK")
        auth.logout = logout

        # client = xmlrpclib.Server()
        client = mock.MagicMock()
        client.auth = auth

        with nested(
                mock.patch('pika.SelectConnection'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.notify'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.send')):

            worker = satellite5worker.Satellite5Worker(
                MQ_CONF,
                logger=self.app_logger)
            worker._on_open(self.connection)
            worker._on_channel_open(self.channel)

            with self.assertRaises(satellite5worker.Satellite5WorkerError):
                result = worker.close_client(client, session_string)

            logout.asser_called_once_with(session_string)

    @mock.patch('replugin.satellite5worker.Satellite5Worker.open_client')
    @mock.patch('replugin.satellite5worker.Satellite5Worker.do_Promote_channel_merge')
    def test_process_good(self, merge, client):
        """The main process method runs notifications when completed"""
        merge.return_value = 1
        client.return_value = ("client", "key")

        with nested(
                mock.patch('pika.SelectConnection'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.notify'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.send'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.verify_config'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.verify_subcommand'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.verify_Promote_params'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.verify_Promote_channels'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.close_client')):

            worker = satellite5worker.Satellite5Worker(
                MQ_CONF,
                logger=self.app_logger,
                config_file='conf/satellite5.json')
            worker._on_open(self.connection)
            worker._on_channel_open(self.channel)

            output = mock.Mock()
            body = {
                'parameters': {
                    'command': 'satellite5',
                    'subcommand': 'Promote'
                },
                'dynamic': {
                    'promote_from_label': 'sourcechannel',
                    'promote_to_label': 'destchannel'
                }
            }
            worker.process(self.channel, self.basic_deliver, self.properties,
                           body, output)

    @mock.patch('replugin.satellite5worker.Satellite5Worker.open_client')
    @mock.patch('replugin.satellite5worker.Satellite5Worker.do_Promote_channel_merge')
    def test_process_bad(self, merge, client):
        """We notice when there's an error while process()ing"""
        merge.side_effect = satellite5worker.Satellite5WorkerError("Couldn't merge")
        client.return_value = ("client", "key")

        with nested(
                mock.patch('pika.SelectConnection'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.notify'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.send'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.verify_config'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.verify_subcommand'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.verify_Promote_params'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.verify_Promote_channels'),
                mock.patch('replugin.satellite5worker.Satellite5Worker.close_client')):

            worker = satellite5worker.Satellite5Worker(
                MQ_CONF,
                logger=self.app_logger,
                config_file='conf/satellite5.json')
            worker._on_open(self.connection)
            worker._on_channel_open(self.channel)

            output = mock.Mock()
            body = {
                'parameters': {
                    'command': 'satellite5',
                    'subcommand': 'Promote'
                },
                'dynamic': {
                    'promote_from_label': 'sourcechannel',
                    'promote_to_label': 'destchannel'
                }
            }
            worker.process(self.channel, self.basic_deliver, self.properties,
                           body, output)

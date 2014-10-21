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

        # server connection
        # self.client = mock.MagicMock('xmlrpclib.Server')

        # self.key = self.client.
        # channel lookup

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
            self.assertEqual(config_good, True)

    def test_verify_satellite_config_bad(self):
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
            self.assertEqual(config_bad, False)

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
            self.assertEqual(result_good, True)

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

    def test_verify_subcommand_parameters(self):
        pass

    def test_open_xmlrpc_connection(self):
        pass

    def test_verify_source_channel(self):
        pass

    def test_verify_target_channel(self):
        pass

    def test_merge_packages(self):
        pass

    def test_logout(self):
        pass

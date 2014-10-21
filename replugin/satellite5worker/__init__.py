# -*- coding: utf-8 -*-
# Copyright © 2014 SEE AUTHORS FILE
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
Satellite 5 worker.
"""

import xmlrpclib

from reworker.worker import Worker


class Satellite5WorkerError(Exception):
    """
    Base exception class for Satellite5Worker errors.
    """
    pass


class Satellite5Worker(Worker):
    """
    Worker which provides basic RPM promotion capabilities
    """

    #: allowed subcommands
    subcommands = ('Promote', )
    dynamic = ['promote_from_label', 'promote_to_label']
    required_config_params = ['satellite_url', 'satellite_login', 'satellite_password']

    def verify_config(self, config):
        """Verify that all required parameters are set in our config file"""
        for key in self.required_config_params:
            if key not in config:
                # Missing key
                return False

        if config['satellite_url'].startswith('http://') or \
           config['satellite_url'].startswith('https://'):
            pass
        else:
            # That probably is not a valid endpoint
            return False

        # Everything checks out. Config is valid.
        return True

    def verify_subcommand(self, parameters):
        """Verify we were supplied with a valid subcommand"""
        subcmd = parameters.get('subcommand', None)
        if subcmd not in self.self.subcommands:
            return False
        else:
            return True

    def verify_Promote_params(self, params):
        """Verify the Promote subcommand was provided all of the the required
parameters

Note: we only expect this worker to support promoting one repository
(copying the contents of) into another. Given that, this method will
break if a new subcommand has dynamic parameters that don't match the
Promote parameters.
        """
        for key in self.dynamic:
            if key not in params:
                # Required key not provided
                return False

        # Got everything we need
        return True

    def open_client(self, config):
        """Create an XMLRPC client to communicate to the Satellite server with"""
        pass

    def verify_Promote_channels(self, client, key, source, destination):
        """Make sure the source and destination channels both exist"""
        pass

    def do_Promote_channel_merge(self, client, key, source, destination):
        """Merge the contents of `source` channel into `destination` channel"""
        pass

    def close_client(self, client, key):
        """Logout and destroy the XMLRPC client"""
        pass

    def process(self, channel, basic_deliver, properties, body, output):
        """Processes Sat5 requests from the bus.

        Verify we have eveything we need to do the needful. Then setup
        the xmlrpc client. Then start doing the needful.

        This assumes we still have just one subcommand, promote
        """
        # Ack the original message
        self.ack(basic_deliver)
        corr_id = str(properties.correlation_id)

        try:
            # Load up the config variables from the json file
            self.verify_config(self._config)

            # Verify valid subcommand
            self.verify_subcommand(body['parameters'])

            # Verify subcmd parameters
            self.verify_Promote_params(body['parameters'])

            # Open connection to remote server and log into it
            (client, key) = self.open_client(self._config)

            # Verify source and target channels exist
            source_channel = body['parameters']['promote_from_label']
            dest_channel = body['parameters']['promote_to_label']
            self.verify_Promote_channels(client, key, source_channel, dest_channel)

            # Merge contents of source into target
            self.do_Promote_channel_merge(client, key, source_channel, dest_channel)

            # Logout
            self.close_client(client, key)
            # Return result

        except Satellite5WorkerError, s5we:
            # If an error happens send a failure and log it to stdout
            self.app_logger.error('Failure: %s' % s5we)
            # Send a message to the FSM indicating a failure event took place
            self.send(
                properties.reply_to,
                corr_id,
                {'status': 'failed'},
                exchange=''
            )
            # Notify over various other comm channels about the event
            self.notify(
                'Satellite 5 Worker Failed',
                str(s5we),
                'failed',
                corr_id)
            # Output to the general logger (taboot tailer perhaps)
            output.error(str(s5we))


def main():  # pragma: no cover
    from reworker.worker import runner
    runner(Satellite5Worker)


if __name__ == '__main__':  # pragma nocover
    main()

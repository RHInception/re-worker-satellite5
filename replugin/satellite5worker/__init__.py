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

    """
    Need to:
        Load up the config variables from the json file

        Verify valid subcommand

        Verify subcmd parameters

        Open connection to remote server

        Verify source and target channels exist

        Merge contents of source into target

        Return result
    """
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
        subcmd = parameters.get('command', None)
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

    def parse_args(self):
        subcommand = str(body['parameters']['subcommand'])
        if subcommand not in self.subcommands:
            raise Satellite5WorkerError(
                'No valid subcommand given. Nothing to do!')

        if subcommand == 'Promote':
            pass

            # if subcommand == 'CherryPickMerge':
            #     self.app_logger.info(
            #         'Executing subcommand %s for correlation_id %s' % (
            #             subcommand, corr_id))
            #     result = self.cherry_pick_merge(body, corr_id, output)
            # else:
            #     self.app_logger.warn(
            #         'Could not the implementation of subcommand %s' % (
            #             subcommand))
            #     raise GitWorkerError('No subcommand implementation')

            # # send results back
            # self.send(
            #     properties.reply_to,
            #     corr_id,
            #     result,
            #     exchange=''
            # )

            # # Notify on result. Not required but nice to do.
            # self.notify(
            #

            # 'GitWorker Executed Successfully',
            #     'GitWorker successfully executed %s. See logs.' % (
            #         subcommand),
            #     'completed',
            #     corr_id)

            # # Send out responses
            # self.app_logger.info(
            #     'GitWorker successfully executed %s for '
            #     'correlation_id %s. See logs.' % (
            #         subcommand, corr_id))

        # except GitWorkerError, fwe:
        #     # If a GitWorkerError happens send a failure log it.
        #     self.app_logger.error('Failure: %s' % fwe)
        #     self.send(
        #         properties.reply_to,
        #         corr_id,
        #         {'status': 'failed'},
        #         exchange=''
        #     )
        #     self.notify(
        #         'GitWorker Failed',
        #         str(fwe),
        #         'failed',
        #         corr_id)
        #     output.error(str(fwe))

    def process(self, channel, basic_deliver, properties, body, output):
        """
        Processes Sat5 requests from the bus.

        *Keys Requires*:
            * subcommand: the subcommand to execute.
        """
        # Ack the original message
        self.ack(basic_deliver)
        corr_id = str(properties.correlation_id)


def main():  # pragma: no cover
    from reworker.worker import runner
    runner(Satellite5Worker)


if __name__ == '__main__':  # pragma nocover
    main()

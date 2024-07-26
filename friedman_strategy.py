# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Author: Steffen70 <steffen@seventy.mx>
# Creation Date: 2024-07-25
#
# Contributors:
# - Contributor Name <contributor@example.com>

import grpc
from concurrent import futures
import time
import json
import os
import sys

# Add the generated directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'generated'))

import playing_field_pb2
import playing_field_pb2_grpc
import strategy_pb2
import strategy_pb2_grpc
import model_pb2

# Environment variable names
CERTIFICATE_SETTINGS_ENV_VAR = "CERTIFICATE_SETTINGS"
FRIEDMAN_PORT_ENV_VAR = "FRIEDMAN_PORT"
PLAYING_FIELD_PORT_ENV_VAR = "PLAYING_FIELD_PORT"

# Servicer class implementing the strategy
class FriedmanStrategyServicer(strategy_pb2_grpc.StrategyServicer):
    def __init__(self):
        self.has_defected = False

    def HandleRequest(self, request, _):
        # Handle the opponent's action
        if request.opponent_action == model_pb2.OpponentAction.DEFECTED:
            self.has_defected = True
        elif request.opponent_action == model_pb2.OpponentAction.NONE:
            self.has_defected = False

        # Prepare the response based on the strategy's state
        response = strategy_pb2.HandleRequestResponse()
        if self.has_defected:
            response.player_action = model_pb2.PlayerAction.DEFECT
        else:
            response.player_action = model_pb2.PlayerAction.COOPERATE

        return response

# Utility function to get environment variables
def get_env_variable(name):
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f"{name} environment variable not set")
    return value

def main():
    # Get certificate settings and ports from environment variables
    cert_settings = json.loads(get_env_variable(CERTIFICATE_SETTINGS_ENV_VAR))
    port = get_env_variable(FRIEDMAN_PORT_ENV_VAR)
    playing_field_port = get_env_variable(PLAYING_FIELD_PORT_ENV_VAR)

    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Add the strategy servicer to the server
    strategy_pb2_grpc.add_StrategyServicer_to_server(FriedmanStrategyServicer(), server)

    # Load the private key and certificate chain for SSL/TLS
    with open(cert_settings['path'] + '.key', 'rb') as f:
        private_key = f.read()
    with open(cert_settings['path'] + '.crt', 'rb') as f:
        certificate_chain = f.read()

    # Create SSL/TLS credentials for the server
    server_credentials = grpc.ssl_server_credentials(((private_key, certificate_chain),))
    server.add_secure_port(f'[::]:{port}', server_credentials)

    print(f'Server listening on port {port}')
    server.start()

    # Create a secure channel to the PlayingField service
    playing_field_channel = grpc.secure_channel(
        f'localhost:{playing_field_port}',
        grpc.ssl_channel_credentials(root_certificates=certificate_chain)
    )
    playing_field_stub = playing_field_pb2_grpc.PlayingFieldStub(playing_field_channel)

    # Create strategy information and subscribe to the PlayingField service
    strategy_info = playing_field_pb2.StrategyInfo(
        name='Friedman',
        address=f'https://localhost:{port}'
    )
    response = playing_field_stub.Subscribe(strategy_info)
    if response.code != grpc.StatusCode.OK:
        raise RuntimeError(f"Failed to subscribe to PlayingField service: {response.details}")

    try:
        # Keep the server running
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        # Stop the server gracefully
        server.stop(0)

if __name__ == '__main__':
    main()

"""
The main script which starts the application.
"""

import sys
import app.tests.client.mocked.run_mocked as run_mocked_client  # pylint: disable=import-error
import app.tests.server.mocked.run_mocked as run_mocked_server  # pylint: disable=import-error
import app.tests.server.unmocked.run_unmocked as run_unmocked_server  # pylint: disable=import-error
from app import app  # pylint: disable=import-error

if __name__ == "__main__":

    # Change index back to 1 before deployment - SME
    if len(sys.argv) > 2 and (sys.argv[1] == "--test" or sys.argv[1] == "-t"):
        test_type = sys.argv[2]
        if test_type == "client_mocked":
            run_mocked_client.run()
        elif test_type == "server_mocked":
            run_mocked_server.run()
        elif test_type == "server_unmocked":
            run_unmocked_server.run()
        else:
            raise ValueError(f'Invalid test type "{test_type}"')
    else:
        app.init_app()
        app.start_app()

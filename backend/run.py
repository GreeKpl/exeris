import eventlet

eventlet.monkey_patch()

import sys

from exeris.app import app, socketio

if len(sys.argv) > 1:
    PORT = int(sys.argv[1])
else:
    PORT = 5000

socketio.run(app, "0.0.0.0", port=PORT)

import sys

from exeris.app import app, socketio

if len(sys.argv) > 1:
    PORT = int(sys.argv[1])
else:
    PORT = 5000

if False:
    socketio.run(app, "0.0.0.0", port=PORT, debug=False)
else:
    socketio.run(app, "127.0.0.1", port=PORT, debug=True)

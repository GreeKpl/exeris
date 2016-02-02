

from exeris.app import app, socketio

if False:
    socketio.run(app, "0.0.0.0", debug=False)
else:
    socketio.run(app, "127.0.0.1", debug=True)

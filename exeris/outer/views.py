# noinspection PyUnresolvedReferences
from exeris.outer import outer_bp, socketio_events


@outer_bp.route("/")
def nic():
    return "OUTER PAGE"

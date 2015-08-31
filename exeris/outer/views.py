from exeris.outer import outer_bp


@outer_bp.route("/")
def nic():
    return "OUTER PAGE"

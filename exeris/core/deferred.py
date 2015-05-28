import base64
import pickle
from exeris.core.main import db


def call(function_to_call):
    function_to_call = pickle.loads(base64.decodebytes(function_to_call.encode("ascii")))

    if type(function_to_call) is tuple:
        function = function_to_call[0]
        return function(*function_to_call[1:])

    raise AssertionError("%s cannot be called as a deferred function".format(str(function_to_call)))


def dumps(*function_call):
    function_call = tuple(function_call)
    return base64.encodebytes(pickle.dumps(function_call)).decode("ascii")


def expected_types(*fun_types):
    def inner(f):
        def g(*args):
            converted_args = [args[0]]
            for arg, arg_type in zip(args[1:], fun_types):

                if arg_type is not None and issubclass(arg_type, db.Model) and type(arg) is int:
                    converted = arg_type.query.get(arg)
                else:
                    converted = arg
                converted_args += [converted]
            return f(*converted_args)
        return g
    return inner

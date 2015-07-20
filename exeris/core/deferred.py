from exeris.core.main import db


def object_import(name):
    parts = name.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


def call(json_to_call, **injected_args):

    if type(json_to_call) is list:
        function_id, kwargs = json_to_call[0], json_to_call[1]

        func = object_import(function_id)
        kwargs.update(injected_args)
        return func(**kwargs)

    raise AssertionError("'{}' is not a list to be called".format(json_to_call))


def convert(**fun_types):
    def inner(f):
        def g(*args, **kwargs):
            converted_args = {}
            for arg_name, arg_value in kwargs.items():

                if arg_name in fun_types and fun_types[arg_name] is not None \
                        and issubclass(fun_types[arg_name], db.Model) and type(arg_value) in (int, str):
                    converted_args[arg_name] = fun_types[arg_name].query.get(arg_value)
                else:
                    converted_args[arg_name] = arg_value

            return f(*args, **converted_args)
        return g
    return inner


class NameInput:
    pass
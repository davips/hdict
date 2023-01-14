from typing import Dict

from hdict import apply, hdict
from hdict.absval import AbsVal
from hdict.lazyval import LazyVal
from hdict.pandas import explode_df
from hdict.param import field, sample, default, val
from hdict.strictval import StrictVal


def handle_values(data:Dict[str, AbsVal | dict]): # REMINDER: 'dict' entries are only "_id" and "_ids".
    newdata  = {}
    dict_of_deps = {}
    for k, v in data.items():
        if isinstance(v, AbsVal):
            newdata[k] = v
        elif isinstance(v, apply):
            # REMINDER: Will just pass a reference for now. May not have all values.
            deps = v.deps__stub()
            dict_of_deps[k] = deps
            newdata[k] = LazyVal(v, deps)
        elif isinstance(v, hdict):
            newdata[k] = StrictVal(v.frozen, v.hosh)
        elif str(type(v)) == "<class 'pandas.core.frame.DataFrame'>":
            newdata[k] = explode_df(v)
        else:
            newdata[k] = StrictVal(v)

    # Fill dependences for 'LazyVal' objects created above.
    for key, deps in dict_of_deps.items():
        for k, v in deps.items():
            match v:
                case field(_, _) | default(_, _) if k in data:
                    v.obj = newdata[k]
                case val(_, _) | default(_, _):
                    v.obj = StrictVal(v.obj)
                case sample(_, _):
                    v.add_dependent(data[key])
                    v.obj = StrictVal(v.obj)
                case _:
                    print(deps.items(), k, v)
                    raise Exception(f"Unknown type for dep_stub entry: '{type(v)}")

    return newdata

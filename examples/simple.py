# `hdict` creation
from hdict import hdict

# From named arguments.
d = hdict(x=5, y=7, z=10)

# From a dict object.
d = hdict({"x": 5, "y": 7, "z": 10})

# From an empty 'hdict' object.
d = hdict() >> {"x": 5} >> {"y": 7, "z": 10}

# All three options have the same result.
d.show(colored=False)
# ...

from hosh import setup

# For better integration within the documentation, we change the color theme.
setup(dark_theme=False)

d.show(colored=False)

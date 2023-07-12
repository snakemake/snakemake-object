__authors__ = ["Johannes Köster", "Maarten Kooyman"]
__copyright__ = "Copyright 2023, Johannes Köster, Maarten Kooyman"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

import collections
from pathlib import Path


class JuliaEncoder:
    """Encoding Python data structures into Julia."""

    @classmethod
    def encode_value(cls, value):
        if value is None:
            return "nothing"
        elif isinstance(value, str):
            return repr(value)
        elif isinstance(value, Path):
            return repr(str(value))
        elif isinstance(value, dict):
            return cls.encode_dict(value)
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, int) or isinstance(value, float):
            return str(value)
        elif isinstance(value, collections.abc.Iterable):
            # convert all iterables to vectors
            return cls.encode_list(value)
        else:
            # Try to convert from numpy if numpy is present
            try:
                import numpy as np

                if isinstance(value, np.number):
                    return str(value)
            except ImportError:
                pass
        raise ValueError(f"Unsupported value for conversion into Julia: {value}")

    @classmethod
    def encode_list(cls, thelist):
        return "[{}]".format(", ".join(map(cls.encode_value, thelist)))

    @classmethod
    def encode_items(cls, items):
        def encode_item(item):
            name, value = item
            return f'"{name}" => {cls.encode_value(value)}'

        return ", ".join(map(encode_item, items))

    @classmethod
    def encode_positional_items(cls, namedlist):
        encoded = ""
        for index, value in enumerate(namedlist):
            encoded += f"{index + 1} => {cls.encode_value(value)}, "
        return encoded

    @classmethod
    def encode_dict(cls, thedict):
        thedict = f"Dict({cls.encode_items(thedict.items())})"
        return thedict

    @classmethod
    def encode_namedlist(cls, namedlist):
        positional = cls.encode_positional_items(namedlist)
        named = cls.encode_items(namedlist.items())
        source = "Dict("
        if positional:
            source += positional
        if named:
            source += named
        source += ")"
        return source

__authors__ = ["Johannes Köster", "Maarten Kooyman"]
__copyright__ = "Copyright 2023, Johannes Köster, Maarten Kooyman"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

import collections
from pathlib import Path


class REncoder:
    """Encoding Python data structures into R."""

    @classmethod
    def encode_numeric(cls, value):
        if value is None:
            return "as.numeric(NA)"
        return str(value)

    @classmethod
    def encode_value(cls, value):
        if value is None:
            return "NULL"
        elif isinstance(value, str):
            return repr(value)
        elif isinstance(value, Path):
            return repr(str(value))
        elif isinstance(value, dict):
            return cls.encode_dict(value)
        elif isinstance(value, bool):
            return "TRUE" if value else "FALSE"
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
                elif isinstance(value, np.bool_):
                    return "TRUE" if value else "FALSE"

            except ImportError:
                pass
        raise ValueError(f"Unsupported value for conversion into R: {value}")

    @classmethod
    def encode_list(cls, thelist):
        return "c({})".format(", ".join(map(cls.encode_value, thelist)))

    @classmethod
    def encode_items(cls, items):
        def encode_item(item):
            name, value = item
            return f'"{name}" = {cls.encode_value(value)}'

        return ", ".join(map(encode_item, items))

    @classmethod
    def encode_dict(cls, thedict):
        thedict = f"list({cls.encode_items(thedict.items())})"
        return thedict

    @classmethod
    def encode_namedlist(cls, namedlist):
        positional = ", ".join(map(cls.encode_value, namedlist))
        named = cls.encode_items(namedlist.items())
        source = "list("
        if positional:
            source += positional
        if named:
            source += ", " + named
        source += ")"
        return source

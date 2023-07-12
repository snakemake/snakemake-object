__authors__ = ["Johannes Köster", "Michael B. Hall"]
__copyright__ = "Copyright 2023, Johannes Köster, Michael B. Hall"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"


from typing import Iterable, List

from snakemake_object.python import SnakemakeObject


class BashEncoder:
    # bash docs for associative arrays -
    # https://www.gnu.org/software/bash/manual/html_node/Arrays.html#Arrays

    def __init__(
        self,
        namedlists: List[str] = None,
        dicts: List[str] = None,
        prefix: str = "snakemake",
    ):
        """namedlists is a list of strings indicating the snakemake object's member
        variables which are encoded as Namedlist.
        dicts is a list of strings indicating the snakemake object's member variables
        that are encoded as dictionaries.
        Prefix is the prefix for the bash variable name(s) e.g., snakemake_input
        """
        if dicts is None:
            dicts = []
        if namedlists is None:
            namedlists = []
        self.namedlists = namedlists
        self.dicts = dicts
        self.prefix = prefix

    def encode_snakemake(self, smk: SnakemakeObject) -> str:
        """Turn a snakemake object into a collection of bash associative arrays"""
        arrays = []
        main_aa = dict()
        for var in vars(smk):
            val = getattr(smk, var)
            if var in self.namedlists:
                aa = (
                    f"{self.prefix}_{var.strip('_').lower()}"
                    f"={self.encode_namedlist(val)}"
                )
                arrays.append(aa)
            elif var in self.dicts:
                aa = f"{self.prefix}_{var.strip('_').lower()}={self.dict_to_aa(val)}"
                arrays.append(aa)
            else:
                main_aa[var] = val

        arrays.append(f"{self.prefix}={self.dict_to_aa(main_aa)}")
        return "\n".join([f"declare -A {aa}" for aa in arrays])

    @staticmethod
    def dict_to_aa(thedict: dict) -> str:
        """Converts a dictionary to an associative array"""
        s = "( "
        for k, v in thedict.items():
            s += f'[{k}]="{v}" '

        s += ")"
        return s

    @classmethod
    def encode_namedlist(cls, named_list) -> str:
        """Convert a namedlist into a bash associative array
        This produces the array component of the variable.
        e.g. ( [var1]=val1 [var2]=val2 )
        to make it a correct bash associative array, you need to name it with
        name=<output of this method>
        """
        aa = "("

        for i, (name, val) in enumerate(named_list._allitems()):
            if isinstance(val, Iterable) and not isinstance(val, str):
                val = " ".join(val)
            aa += f' [{i}]="{val}"'
            if name is not None:
                aa += f' [{name}]="{val}"'

        aa += " )"
        return aa

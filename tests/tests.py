from snakemake.io import InputFiles, Log
from snakemake_object.bash import BashEncoder
import pandas as pd

import pytest
from snakemake_object.julia import JuliaEncoder
from snakemake_object.python import SnakemakeObject
from snakemake_object.r import REncoder


@pytest.fixture
def example_namedlist():
    f = InputFiles(fromdict={"foo": "test.in", "bar": "named.in"})
    f.append("test2.txt")
    return f


@pytest.fixture
def example_log():
    return Log(["test.log"])


@pytest.fixture
def example_dict():
    return {
        "foo": 1,
        "bar": None,
        "baz": "test",
        "float": 1.2,
        "pandas": pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}),
    }


@pytest.fixture
def example_list():
    return [1, 2, 3, None, pd.Series([1, 2, 3])]


def test_bash_named_list_one_named_one_str(self):
    """InputFiles is a subclass of snakemake.io.NamedInput
    ierate over input and store each with the integer index - i.e 0, 1, 2
    then use input.items() to iterate over the named files and store them as named also
    check how this works with named things being lists
    """
    named_list = InputFiles(["test.in", "named.in"])
    named_list._set_name("named", 1)

    actual = BashEncoder.encode_namedlist(named_list)
    expected = r"""( [0]="test.in" [1]="named.in" [named]="named.in" )"""

    assert actual == expected


def test_bash_named_list_named_is_list(self):
    """Named lists that are lists of files become a space-separated string as you
    can't nest arrays in bash"""
    named_list = InputFiles(["test1.in", ["test2.in", "named.in"]])
    named_list._set_name("named", 1)

    actual = BashEncoder.encode_namedlist(named_list)
    expected = (
        r"""( [0]="test1.in" [1]="test2.in named.in" [named]="test2.in named.in" )"""
    )

    assert actual == expected


def test_python_object(example_namedlist, example_dict, example_log):
    o = SnakemakeObject(
        input_=example_namedlist,
        output=example_namedlist,
        params=example_namedlist,
        wildcards=example_namedlist,
        threads=1,
        resources=example_namedlist,
        log=example_log,
        config=example_dict,
        rulename="foo",
        bench_iteration=1,
        scriptdir=None,
    )
    assert o.log_fmt_shell() == "2> test.log"


def test_r_object(example_namedlist, example_dict, example_list):
    REncoder.encode_list(example_list)
    REncoder.encode_dict(example_dict)
    REncoder.encode_namedlist(example_namedlist)


def test_julia_object(example_namedlist, example_dict, example_list):
    JuliaEncoder.encode_list(example_list)
    JuliaEncoder.encode_dict(example_dict)
    JuliaEncoder.encode_namedlist(example_namedlist)


def test_bash_object(example_namedlist):
    BashEncoder.encode_namedlist(example_namedlist)

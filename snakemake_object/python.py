import os
from pathlib import Path
from typing import Optional, Union

PathLike = Union[str, Path, os.PathLike]


class SnakemakeObject:
    def __init__(
        self,
        input_,
        output,
        params,
        wildcards,
        threads,
        resources,
        log,
        config,
        rulename,
        bench_iteration,
        scriptdir=None,
    ):
        # convert input and output to plain strings as some remote objects cannot
        # be pickled
        self.input = input_.plainstrings()
        self.output = output.plainstrings()
        self.params = params
        self.wildcards = wildcards
        self.threads = threads
        self.resources = resources
        self.log = log.plainstrings()
        self.config = config
        self.rule = rulename
        self.bench_iteration = bench_iteration
        self.scriptdir = scriptdir

    def log_fmt_shell(self, stdout=True, stderr=True, append=False):
        """
        Return a shell redirection string to be used in `shell()` calls

        This function allows scripts and wrappers to support optional `log` files
        specified in the calling rule.  If no `log` was specified, then an
        empty string "" is returned, regardless of the values of `stdout`,
        `stderr`, and `append`.

        Parameters
        ---------

        stdout : bool
            Send stdout to log

        stderr : bool
            Send stderr to log

        append : bool
            Do not overwrite the log file. Useful for sending an output of
            multiple commands to the same log. Note however that the log will
            not be truncated at the start.

        The following table describes the output:

        -------- -------- -------- ----- -------------
        stdout   stderr   append   log   return value
        -------- -------- -------- ----- ------------
        True     True     True     fn    >> fn 2>&1
        True     False    True     fn    >> fn
        False    True     True     fn    2>> fn
        True     True     False    fn    > fn 2>&1
        True     False    False    fn    > fn
        False    True     False    fn    2> fn
        any      any      any      None  ""
        -------- -------- -------- ----- -----------
        """
        return _log_shell_redirect(self.log, stdout, stderr, append)


def _log_shell_redirect(
    log: Optional[PathLike],
    stdout: bool = True,
    stderr: bool = True,
    append: bool = False,
) -> str:
    """
    Return a shell redirection string to be used in `shell()` calls

    This function allows scripts and wrappers support optional `log` files
    specified in the calling rule.  If no `log` was specified, then an
    empty string "" is returned, regardless of the values of `stdout`,
    `stderr`, and `append`.

    Parameters
    ---------

    stdout : bool
        Send stdout to log

    stderr : bool
        Send stderr to log

    append : bool
        Do not overwrite the log file. Useful for sending output of
        multiple commands to the same log. Note however that the log will
        not be truncated at the start.

    The following table describes the output:

    -------- -------- -------- ----- -------------
    stdout   stderr   append   log   return value
    -------- -------- -------- ----- ------------
    True     True     True     fn    >> fn 2>&1
    True     False    True     fn    >> fn
    False    True     True     fn    2>> fn
    True     True     False    fn    > fn 2>&1
    True     False    False    fn    > fn
    False    True     False    fn    2> fn
    any      any      any      None  ""
    -------- -------- -------- ----- -----------
    """
    if not log:
        return ""
    lookup = {
        (True, True, True): " >> {0} 2>&1",
        (True, False, True): " >> {0}",
        (False, True, True): " 2>> {0}",
        (True, True, False): " > {0} 2>&1",
        (True, False, False): " > {0}",
        (False, True, False): " 2> {0}",
    }
    return lookup[(stdout, stderr, append)].format(str(log))

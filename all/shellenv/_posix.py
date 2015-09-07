# coding: utf-8
from __future__ import unicode_literals, division, absolute_import, print_function

import os
import sys
import subprocess
from getpass import getuser

from ._types import str_cls, type_name

if sys.platform == 'darwin':
    from ._osx.open_directory import get_user_login_shell
else:
    from ._linux.getent import get_user_login_shell



_envs = {}
_environ = {}
for key in ('HOME', 'LANG', 'USER', 'PATH'):
    if key in os.environ:
        _environ[key] = os.environ[key]


def get_shell_env(shell=None):
    """
    Fetches the environmental variables that are set when a new shell is opened.

    :param shell:
        The shell to get the env from, if None, uses the current user's login
        shell

    :return:
        A 2-element tuple:
         - [0] unicode string shell path
         - [1] env dict with keys and values as unicode strings
    """

    if shell is not None and not isinstance(shell, str_cls):
        raise TypeError('shell must be a unicode string, not %s' % type_name(shell))

    if shell is None:
        shell = get_user_login_shell(get_user())
    _, shell_name = shell.rsplit('/', 1)

    if shell not in _envs:
        params = ['-i', '-c', '/usr/bin/env']
        if shell_name not in ['tcsh', 'csh']:
            params.insert(0, '-l')
        params.insert(0, shell)

        env_proc = subprocess.Popen(
            params,
            stdin=None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=_environ,
            close_fds=True
        )

        stdout, _ = env_proc.communicate()

        if shell not in _envs:
            _envs[shell] = {}

        entries = stdout.strip().split(b'\n')
        for entry in entries:
            parts = entry.split(b'=', 1)
            name = parts[0].decode('utf-8', 'replace')
            value = parts[1].decode('utf-8', 'replace')
            _envs[shell][name] = value

    return (shell, _envs[shell])


def get_user():
    """
    Returns the current username as a unicode string

    :return:
        A unicode string of the current user's username
    """

    output = getuser()
    if not isinstance(output, str_cls):
        output = output.decode('utf-8')
    return output

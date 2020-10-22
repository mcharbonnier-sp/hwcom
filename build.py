import os
import re
import shutil
import subprocess as sp
from typing import List

from src.version import VERSION as version
from src.version import NAME as name

build_path = os.path.join('.', 'build')
software = f'{name}_{version}'
output = os.path.join(build_path, software)
ignored_ext = ['.pyc', '.pyo', '.log', '.png']
ignored_dirs = [build_path, os.path.join('.', 'plugins'), os.path.join('.', 'debug')]
ignored_py = [os.path.join('.', 'build.py'), os.path.join('.', 'debug.py')]


def call_suprocess(command: List[str], timeout=15):
    p = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE)
    try:
        out, err = p.communicate(timeout=15)
    except sp.TimeoutExpired:
        p.kill()
        out, err = p.communicate()
    return out, err


def build_version():
    has_changes = False
    out, err = call_suprocess('git status -b -uno --porcelain'.split(' '))
    out = out.decode('utf8')
    lines = out.split('\n')
    m = re.match(r'## (?P<branch>[\w]+)\.\.\.(?P<remote>[\w]+)/(?P<r_branch>[\w]+)(\s+\[(?P<diff>(ahead)|(behind))\s+[0-9]+])?', lines[0])
    if m is None:
        raise RuntimeError(f'Could not get git status\n'
                           f'Git output:\n'
                           f'{out}'
                           f'stderr:'
                           f'{err.decode("utf8")}')
    if len(lines) > 1:
        has_changes = True
    gd = m.groupdict()
    ahead = gd['diff'] == 'ahead'
    remote = gd['remote']
    remote_branch = gd['r_branch']

    out, err = call_suprocess('git rev-parse HEAD'.split(' '))
    if not out:
        raise RuntimeError(f'Could not get git commit hash\n'
                           f'Git output:\n'
                           f'{out}'
                           f'stderr:'
                           f'{err.decode("utf8")}')
    commit = out.decode('utf8').strip()

    out, err = call_suprocess(f'git remote get-url {remote}'.split(' '))
    if not out:
        raise RuntimeError(f'Could not get remote url\n'
                           f'Git output:\n'
                           f'{out}'
                           f'stderr:'
                           f'{err.decode("utf8")}')

    remote_url = out.decode('utf8').strip()

    with open(os.path.join(output, 'version.py'), 'w') as f:
        f.write(f'NAME = "{name}"\n'
                f'VERSION = "{version}"\n'
                f'GIT_COMMIT = "{commit}"\n'
                f'GIT_REMOTE = "{remote_url}"\n'
                f'GIT_BRANCH = "{remote_branch}"\n'
                f'GIT_MODIFIED = {has_changes}\n'
                f'GIT_AHEAD = {ahead}\n')


def is_ignored(directory, content):
    """
    :param str directory:
    :param list[str] content:
    :return:
    """
    ignored = []
    for p in content:
        full_path = os.path.join(directory, p)
        if p.startswith('.'):
            ignored.append(p)
        elif full_path in ignored_dirs:
            ignored.append(p)
        elif full_path in ignored_py:
            ignored.append(p)
        elif os.path.splitext(p)[1].lower() in ignored_ext:
            ignored.append(p)
    return ignored


try:
    shutil.rmtree(output)
except WindowsError as ec:
    if ec.errno == 2:
        pass
    else:
        print('Could not remove the output path:\n{0}'.format(output))
        print(ec)
        raise
except Exception as ec:
    print('Could not remove the output path:\n{0}'.format(output))
    print(ec)
    raise

try:
    os.makedirs(build_path)
except WindowsError as ec:
    if ec.errno == 17:
        pass
    else:
        print('Could not remove the output path:\n{0}'.format(output))
        print(ec)
        raise
except Exception as ec:
    print('Creation of the destination directory failed:\n{0}'.format(output))
    print(ec)
    raise

shutil.copytree('./src', output, ignore=is_ignored)
build_version()

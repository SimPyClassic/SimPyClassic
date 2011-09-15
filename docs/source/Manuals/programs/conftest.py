# coding=utf-8

import os.path
import subprocess

import pytest

def pytest_collect_file(path, parent):
    if path.ext != '.py': return
    root, ext = os.path.splitext(str(path))
    if not os.path.exists(root + '.OK'): return
    return TutorialFile(path, parent)


class TutorialFile(pytest.File):
    def collect(self):
        yield TutorialItem(str(self), self)


class TutorialItem(pytest.Item):
    def runtest(self):
        root, ext = os.path.splitext(str(self.fspath))
        with open(root + '.OK') as f:
            expected = f.read()
        output = subprocess.check_output(['python', str(self.fspath)])
        assert output == expected


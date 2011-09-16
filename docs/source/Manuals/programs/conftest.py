# coding=utf-8

import os.path
import subprocess

import pytest
from py._code.code import TerminalRepr, ReprFileLocation
from _pytest.assertion.util import _diff_text


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
        output = subprocess.check_output(['python', str(self.fspath)],
                stderr=subprocess.STDOUT)
        if output != expected:
            raise ValueError(expected, output)

    def repr_failure(self, exc_info):
        if exc_info.errisinstance((ValueError,)):
            expected, output = exc_info.value.args
            message = _diff_text(expected, output)
            return ReprFailTutorial(self.fspath.basename, message)
        elif exc_info.errisinstance((subprocess.CalledProcessError,)):
            return ReprErrorTutorial(self.fspath.basename, exc_info)
        else:
            return pytest.Item.repr_failure(self, exc_info)

    def reportinfo(self):
        return self.fspath, None, '[tutorial %s]' % self.fspath.basename


class ReprFailTutorial(TerminalRepr):
    Markup = {
            '+': dict(green=True),
            '-': dict(red=True),
            '?': dict(bold=True),
    }

    def __init__(self, filename, message):
        self.filename = filename
        self.message = message

    def toterminal(self, tw):
        for line in self.message:
            markup = ReprFailTutorial.Markup.get(line[0], {})
            tw.line(line, **markup)
        tw.line('%s: Unexpected output' % self.filename)


class ReprErrorTutorial(TerminalRepr):
    def __init__(self, filename, exc_info):
        self.filename = filename
        self.exc_info = exc_info

    def toterminal(self, tw):
        tw.line('Execution failed! Captured output:', bold=True)
        tw.sep('-')
        tw.line(self.exc_info.value.output, red=True, bold=True)
        tw.line('%s: Tutorial failed (exitcode=%d)' % (self.filename,
                self.exc_info.value.returncode))

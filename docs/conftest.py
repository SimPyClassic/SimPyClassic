# coding=utf-8

import os.path
import subprocess

import pytest
from py._code.code import TerminalRepr, ReprFileLocation
from _pytest.assertion.util import _diff_text


blacklist = ['SimRTManual.rst']


def pytest_collect_file(path, parent):
    if path.ext != '.rst': return
    for item in blacklist:
        if str(path).endswith(item): return
    return ExampleFile(path, parent)


class ExampleFile(pytest.File):
    def collect(self):
        # Collect all literal includes.
        literalincludes = []
        with self.fspath.open() as data:
            for lineno, line in enumerate(data):
                if 'literalinclude' not in line: continue
                filename = line.split('::')[-1].strip()
                filepath = os.path.join(self.fspath.dirname, filename)
                if not os.path.exists(filepath): continue
                literalincludes.append((lineno, filename))

        # Check for directly following output specification.
        for idx in range(len(literalincludes) - 1):
            example_lineno, example = literalincludes[idx]
            output_lineno, output = literalincludes[idx+1]
            if not example.endswith('.py'): continue
            if not output.endswith('.out'): continue
            yield ExampleItem(output_lineno, example, output, self)


class ExampleItem(pytest.Item):
    def __init__(self, lineno, example, output, parent):
        pytest.Item.__init__(self, example, parent)
        self.lineno = lineno
        self.example = example
        self.output = output
        self.examplefile = os.path.join(self.fspath.dirname, self.example)
        self.outputfile = os.path.join(self.fspath.dirname, self.output)

    def runtest(self):
        with open(self.outputfile) as f:
            expected = f.read()
        output = subprocess.check_output(['python', self.examplefile],
                stderr=subprocess.STDOUT)
        if output != expected:
            raise ValueError(expected, output)

    def repr_failure(self, exc_info):
        if exc_info.errisinstance((ValueError,)):
            expected, output = exc_info.value.args
            message = _diff_text(expected, output)
            return ReprFailExample(self.fspath.basename, self.lineno,
                    self.outputfile, message)
        elif exc_info.errisinstance((subprocess.CalledProcessError,)):
            return ReprErrorExample(self.fspath.basename, self.lineno,
                    self.examplefile, exc_info)
        else:
            return pytest.Item.repr_failure(self, exc_info)

    def reportinfo(self):
        return self.fspath, None, '[example %s]' % (
                os.path.relpath(self.examplefile))


class ReprFailExample(TerminalRepr):
    Markup = {
            '+': dict(green=True),
            '-': dict(red=True),
            '?': dict(bold=True),
    }

    def __init__(self, filename, lineno, outputfile, message):
        self.filename = filename
        self.lineno = lineno
        self.outputfile = outputfile
        self.message = message

    def toterminal(self, tw):
        for line in self.message:
            markup = ReprFailExample.Markup.get(line[0], {})
            tw.line(line, **markup)
        tw.line('%s:%d (in %s): Unexpected output' % (self.filename,
                self.lineno, os.path.relpath(self.outputfile)))


class ReprErrorExample(TerminalRepr):
    def __init__(self, filename, lineno, examplefile, exc_info):
        self.filename = filename
        self.lineno = lineno
        self.examplefile = examplefile
        self.exc_info = exc_info

    def toterminal(self, tw):
        tw.line('Execution failed! Captured output:', bold=True)
        tw.sep('-')
        tw.line(self.exc_info.value.output, red=True, bold=True)
        tw.line('%s:%d (%s) Example failed (exitcode=%d)' % (self.filename,
                self.lineno, os.path.relpath(self.examplefile),
                self.exc_info.value.returncode))

import os, sys
from glob import glob
from pprint import pprint
from datetime import datetime
from collections import defaultdict

import numpy as np
from tabulate import tabulate

from .system import *


##################################################################################
class Statistics(object):
    def __init__(self):
        self.d = defaultdict(list)
        self.w = defaultdict(list)

    def add(self, k, v, w=1):
        self.d[k].append(v)
        self.w[k].append(w)

    def mean(self, k):
        d = np.array(self.d[k])
        w = np.array(self.w[k])
        return np.sum(d * w) / np.sum(w)

    def min(self, k):
        return np.min(self.d[k])

    def max(self, k):
        return np.max(self.d[k])

    def __getitem__(self, k):
        assert k in self.d
        return self.d[k], self.w[k]

    def __setitem__(self, k, v):
        self.d[k], self.w[k] = v

    def __iter__(self):
        for k in self.d: yield k

    def __repr__(self):
        return self.to_string()

    def to_string(self, verbose=False):
        if not verbose:
            return '[' + ', '.join([f'{k} = {self.mean(k)}' for k in self]) + ']'
        else:
            data = []
            for k in self:
                data.append([k, self.mean(k), self.max(k), self.min(k)])
            return '\n\n' + tabulate(data, headers=['Metric', 'Average', 'Max', 'Min']) + '\n\n'

    def items(self):
        return self.d.items()

    def log_tensorboard(self, tb, step):
        for k in self:
            tb.add_scalar(k, self.mean(k), step)


##################################################################################
class Printer(object):
    def __init__(self, logfile=None, mode='w', stdout=True):
        self.logfile = logfile
        self.fout = None
        self.mode = mode
        if stdout: print('Logging to:', self.logfile)


    def now(self):
        return datetime.now().strftime('%b-%d-%y@%H:%M:%S')


    def open(self):
        if self.fout is None:
            mkdir(os.path.dirname(self.logfile))
            self.fout = open(self.logfile, self.mode)


    def fprint(self, *args, **kwargs):
        self.open()

        now = f'{self.now():25}'

        for fp in [self.fout]:
            print(now, *args, **kwargs, file=fp)
            fp.flush()


    def print(self, *args, **kwargs):
        self.open()

        now = f'{self.now():25}'

        for fp in [sys.stdout, self.fout]:
            print(now, *args, **kwargs, file=fp)
            fp.flush()


    def pprint(self, python_dict, stdout=True):
        self.open()

        now = f'{self.now():25}'

        for fp in ([sys.stdout, self.fout] if stdout else [self.fout]):
            pprint(python_dict, fp)
            fp.flush()

    def __contains__(self, key):
        return hasattr(self, key)

    def items(self):
        return vars(self).items()

    def update(self, d):
        for k, v in d.items():
            setattr(self, k, v)

    def get(self, key, default_value):
        return vars(self).get(key, default_value)


##################################################################################
def save_codes(pattern, target_dir):
    mkdir(target_dir)

    for filename in glob(pattern):
        basename = os.path.basename(filename)

        with open(filename) as fin, \
             open(f'{target_dir}/{basename}', 'w') as fout:
            fout.write(fin.read())


def latest_checkpoint(ckpt_dir, pattern='*', basename=False):
    ret = max(glob(f'{ckpt_dir}/{pattern}'), key=os.path.getctime)
    if basename:
        ret = os.path.basename(ret)
    return ret
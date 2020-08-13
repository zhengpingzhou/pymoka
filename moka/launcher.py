# FIXME(zpzhou): Ugly! CLean this file!

import re
import argparse
import subprocess

from tabulate import tabulate

from .core import *
from .system import *


if __name__ == '__main__':
    MARKER = '##'

    EXP = sys.argv[1]

    if len(sys.argv) > 2:
        CMD = sys.argv[2]
    else:
        CMD = None

    if len(sys.argv) > 3:
        TARGET = sys.argv[3]
        assert sys.argv[2] == '--'

    if EXP == 'ls':
        ps = subprocess.check_output(['ps', 'aux'])
        procs = [line for line in ps.decode('utf-8').split('\n') if line.strip()]
        nfields = len(procs[0].split()) - 1

        jobs = []
        for row in procs[1:]:
            j = Dict()
            j.user, j.pid, j.cpu, j.mem, *_, j.start_time, j.wall_time, j.command = row.split(None, nfields)
            j.command = j.command.strip()
            if j.user != g.USER: continue
            jobs.append(j)

        moka_ids = []
        for j in jobs:
            found = re.findall(r'python -m moka.launcher (.+) train', j.command)
            if found:
                moka_ids.append(found[0])

        python_jobs = []
        for moka_id in moka_ids:
            python_job = None
            for j in jobs:
                if re.findall(f'python .* -id {moka_id} .*', j.command):
                    python_job = j 
                    j.moka_id = moka_id
                    break
            python_jobs.append(python_job)

        table = [(j.user, j.pid, j.cpu, j.mem, j.start_time, j.wall_time, j.moka_id, j.command[:30] + ('...' if len(j.command) > 30 else '')) for j in python_jobs]
        print(tabulate(table, ['User', 'PID', '%CPU', '%MEM', 'START', 'TIME', 'ID', 'Command'], tablefmt="fancy_grid"))

        sys.exit()


    if CMD is None:
        sys.exit()

    config_path = f'configs/{EXP}.sh'

    # parse
    with open(config_path) as fp:

        config = dict()
        option = dict()
        command = None

        for line in fp.readlines():

            if line.startswith(MARKER):
                command = line.replace(MARKER, '').strip()
                commands = command.split(' ')
                command = commands[0]

                parser = argparse.ArgumentParser()
                parser.add_argument('--silent', action='store_true')
                opt = parser.parse_args(commands[1:])

                config[command] = []
                option[command] = opt

            else:
                config[command].append(line) 

        if CMD == '--':
            file = f'configs/{TARGET}.sh'
            if (not os.path.isfile(file)) or ask(f'File {file} exists. Overwrite?'):
                shell(f'cp configs/{EXP}.sh {file}', verbose=False)

        elif CMD not in config:
            raise ValueError(f'Command "{CMD}" not found in experiment {EXP} ({config_path})!')

        else:
            if 'common' in config:
                REGEX_EXP = r'EXP="(.+)"'
                REGEX_ID = r'ID="(.+)"'
                for line in config['common']:
                    found_exp = re.findall(REGEX_EXP, line)
                    found_id = re.findall(REGEX_ID, line)
                    if found_exp:
                        COMMON_EXP = found_exp[0]
                    elif found_id:
                        COMMON_ID = found_id[0]

                COMMON_ID = COMMON_ID.replace('${EXP}', COMMON_EXP)      
                if COMMON_ID != EXP and ask(f'ID `{COMMON_ID}` != filename `{EXP}`, continue?') != 'y':
                    sys.exit(-1)

            script = ''.join(config.get('common', '')) + '\n' + ''.join(config[CMD])
            shell(script, verbose=not option[CMD].silent)

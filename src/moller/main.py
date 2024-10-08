import os,sys
import re
#import datetime
#import yaml
import ruamel.yaml as yaml

from moller import __version__
from moller.platform.base import Platform, create_platform

import logging
logger = logging.getLogger(__name__)

class TaskSerial:
    def __init__(self, name, info, platform):
        self.name = name
        self.info = info
        self.platform = platform
        self.setup(info)

    def setup(self, info):
        if info is None:
            self.code = None
        else:
            if 'code' in info:
                self.code = info['code']
            elif 'run' in info:
                self.code = info['run']
            else:
                self.code = None

    def generate(self, fp):
        logger.info('TaskSerial: name={}'.format(self.name))
        if self.code is not None:
            fp.write("#-------- {} --------\n".format(self.name))
            fp.write(self.code)
            fp.write('\n')

class TaskParallel:
    def __init__(self, name, info, platform):
        self.name = name
        self.info = info
        self.platform = platform

        self.prev_log_file = None
        self.setup(info)

    def setup(self, info):
        if info is None:
            return
        node = info.get('node', [])
        if type(node) is list:
            if len(node) == 0:
                node = [1,1,1]
            elif len(node) == 1:
                node = node + [1,1]
            elif len(node) == 2:
                node = [0] + node
            else:
                node = node[0:3]
        elif type(node) is int:
            node = [node,1,1]
        else:
            msg = 'node must be scalar or list'
            logger.error(msg)
            raise ValueError(msg)
        self.node = node

        self.func_name = 'task_{}'.format(self.name)
        self.log_file = 'stat_{}.dat'.format(self.name)
        self.prev_log_file = info.get('prev_log_file', None)

        self.code = info.get('run', '')

    def generate(self, fp):
        logger.info('TaskParallel: name={}'.format(self.name))

        srun_str = self.platform.parallel_command({'node': self.node})

        # run = self.code
        # run = re.sub(r'\n$','', run)
        # run = re.sub(r'(srun|mpirun|mpiexec)', srun_str, run)
        # run = re.sub(r'^',r'  ', run)
        # run = re.sub(r'\n',r'\n  ', run)

        lines = self.code.splitlines()
        lines_new = []
        for line in lines:
            if re.search(r'\b(srun|mpirun|mpiexec)\b', line):
                line = re.sub(r'(srun|mpirun|mpiexec)', srun_str, line)

                lines_new.append(r'  DEBUG "$_work_item: ' + line + '"')
                # line = re.sub(r'^', '  ', line)
                lines_new.append(line)
            else:
                # line = re.sub(r'^', '  ', line)
                lines_new.append(line)
        run = '\n'.join(lines_new)

        func_lines = []
        func_lines.append(('function {} ()'.format(self.func_name)) + ' {')
        func_lines.append('\n'.join([
            '  set -e',
            '  _sig=$1',
            '  _work_item=$2',
            '  _slot_id=$3',
            '  _workdir=$_work_item',
            '',
            '  _s=(${_sig//,/ })',
            '  _nn=${_s[0]}',
            '  _np=${_s[1]}',
            '  _nc=${_s[2]}',
            '',
            '  _setup_taskenv',
            '']))

        if self.prev_log_file is not None:
            func_lines.append('  if ! _is_ready $_work_item {}; then'.format(self.prev_log_file))
            func_lines.append('    exit -1')
            func_lines.append('  fi')
        func_lines.append('  cd $_workdir')
        func_lines.append('')
        func_lines.append(run)
        func_lines.append('}')
        func_lines.append('export -f {}\n'.format(self.func_name))

        par_sig = ','.join([str(i) for i in self.node])
        
        exec_lines = []
        exec_lines.append('date')
        exec_lines.append('echo "  {}"'.format(self.name))
        exec_lines.append(r"printf '%s\n' ${mplist[@]} | run_parallel" + (' {} {} {}'.format(par_sig, self.func_name, self.log_file)))

        fp.write("#-------- {} --------\n".format(self.name))
        fp.write('\n'.join(func_lines) + '\n')
        fp.write('\n'.join(exec_lines) + '\n')
        fp.write('\n')

class ScriptGenerator:
    def __init__(self, info):
        self.info = info
        self.setup(info)

    def setup(self, info):
        self.name = info.get('name', None)
        self.desc = info.get('description', None)
        self.output_file = info.get('output_file', None)

        platform_info = info.get('platform', None)
        self.platform = create_platform(platform_info.get("system", None), platform_info)
        if self.platform.job_name is None:
            self.platform.job_name = self.name

        prologue = TaskSerial('prologue', info.get('prologue', None), self.platform)
        epilogue = TaskSerial('epilogue', info.get('epilogue', None), self.platform)

        func_def = TaskSerial('function_definitions', {
            'code': self.platform.generate_function()
        }, self.platform)

        self.tasklist = []
        prev_log_file = None
        log_file_list = []

        jobs = info.get('jobs', {})
        for task_name, task_info in jobs.items():
            task_type = task_info.get('parallel', True)
            if task_type:
                task_info.update({'prev_log_file': prev_log_file})
                task = TaskParallel(task_name, task_info, self.platform)
                prev_log_file = task.log_file
                log_file_list.append(task.log_file)
            else:
                task = TaskSerial(task_name, task_info, self.platform)
            self.tasklist.append(task)

        check_logfile = TaskSerial('check_logfile', {
            'code': self.generate_check_logfile(log_file_list)
        }, self.platform)

        self.tasklist.insert(0, prologue)
        self.tasklist.insert(1, func_def)
        self.tasklist.insert(2, check_logfile)
        self.tasklist.append(epilogue)
    
    def generate(self, fp):
        self.platform.generate_header(fp)
        for task in self.tasklist:
            task.generate(fp)

    def generate_check_logfile(self, log_file_list):
        func_lines = []
        func_lines.append('if [ $retry -gt 0 ]; then\n    :\nelse')
        func_lines.append('    _logfile_count=0')
        for log_file in log_file_list:
            func_lines.append('    if [ -f {} ]; then\n        _logfile_count=$((_logfile_count + 1))\n        # echo "INFO: status file {} found."\n    fi'.format(log_file, log_file))
        func_lines.append('    if [ $_logfile_count -gt 0 ]; then')
        func_lines.append('        echo "INFO: job status file found. make sure it is resume/retry run."')
        func_lines.append('    fi')
        func_lines.append('fi')
        return '\n'.join(func_lines) + '\n'

def run(*, info_file = None, info_dict = None, output = None):
    if info_dict is None and info_file is None:
        msg = 'run: neither info_file and info_dict specified.'
        logger.error(msg)
        raise RuntimeError(msg)
    if info_dict is not None and info_file is not None:
        msg = 'run: both info_file and info_dict specified.'
        logger.error(msg)
        raise RuntimeError(msg)
    if info_file is not None:
        try:
            with open(info_file, "r") as fp:
                info_dict = yaml.safe_load(fp)
        except yaml.YAMLError as e:
            msg = 'run: yaml error: {}'.format(e)
            logger.error(msg)
            raise RuntimeError(msg)
        except Exception as e:
            msg = 'run: {}'.format(e)
            logger.error(msg)
            raise RuntimeError(msg)

    scriptgen = ScriptGenerator(info_dict)

    if output is not None:
        pass
    elif scriptgen.output_file is not None:
        output = scriptgen.output_file

    if output is not None:
        with open(output, "w") as fp:
            scriptgen.generate(fp)
    else:
        scriptgen.generate(sys.stdout)

def main():
    import argparse

    parser = argparse.ArgumentParser(prog='moller')
    parser.add_argument('input_yaml', nargs='?', default=None, help='task description file')
    parser.add_argument('-o', '--output', nargs='?', default=None, help='output file')
    parser.add_argument('--version', action='store_true', help='show version')

    args = parser.parse_args()

    if args.version:
        print('moller', __version__)
        sys.exit(0)

    if args.input_yaml is None:
        parser.print_help()
        sys.exit(1)

    run(info_file = args.input_yaml, output = args.output)

if __name__ == '__main__':
    main()

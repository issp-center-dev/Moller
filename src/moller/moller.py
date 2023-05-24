import os,sys
import re
import datetime
import yaml
#import ruamel.yaml as yaml

import logging
logger = logging.getLogger(__name__)

def convert_hhmmss_to_seconds(x):
    s = 0
    for v in x.split(':'):
        s = s * 60 + int(v, 10)
    return s

def convert_seconds_to_hhmmss(x):
    return datetime.timedelta(seconds=x)

class Platform:
    def __init__(self, info):
        pass

    def batch_queue_setup(self, info):
        if 'queue' not in info:
            msg = 'queue not specified'
            logger.error(msg)
            raise ValueError(msg)
        self.queue = info.get('queue', None)

        if 'node' not in info:
            msg = 'node not specified'
            logger.warning(msg)
        node = info.get('node', 1)
        nnode = node[0] if type(node) is list else node
        self.node = node
        self.nnode = nnode

        if 'elapsed' not in info:
            msg = 'elapsed time not specified'
            logger.warning(msg)
        self.elapsed = convert_hhmmss_to_seconds(info.get('elapsed', '0'))

        if 'job_name' in info:
            self.job_name = info['job_name']
        else:
            self.job_name = None
        
    def generate(self, fp):
        pass

    @classmethod
    def create(cls, info):
        if info is None:
            return DefaultPlatform.create(info)
        else:
            plt = info.get('system', None)
            if plt == 'ohtaka':
                return Ohtaka.create(info)
            else:
                raise ValueError('unknown system type: {}'.format(plt))

class Ohtaka(Platform):
    def __init__(self, info):
        super().__init__(info)
        self.setup(info)

    def setup(self, info):
        super().batch_queue_setup(info)

    def parallel_command(self, info):
        node = info.get('node', None)
        cmd = r'srun --exclusive -N {} -n {} -c {}'.format(*node)
        return cmd

    def generate_header(self, fp):
        shebang = '#!/bin/bash\n'

        sched_key = '#SBATCH '

        sched_params = []
        sched_params.append(sched_key + ('-p {}'.format(self.queue)))
        sched_params.append(sched_key + ('-N {}'.format(self.nnode)))
        sched_params.append(sched_key + ('-t {}'.format(convert_seconds_to_hhmmss(self.elapsed))))
        if self.job_name is not None:
            sched_params.append(sched_key + ('-J {}'.format(self.job_name)))

        fp.write(shebang)
        fp.write('\n'.join(sched_params) + '\n')
        fp.write('\n')

    @classmethod
    def create(cls, info):
        return cls(info)

class DefaultPlatform(Platform):
    def __init__(self, info):
        super().__init__(info)
        pass
    @classmethod
    def create(cls, info):
        return cls(info)

class TaskSerial:
    def __init__(self, name, info, platform):
        self.name = name
        self.info = info
        self.platform = platform
        self.setup(info)

    def setup(self, info):
        if 'code' in info:
            self.code = info['code']
        elif 'run' in info:
            self.code = info['run']
        else:
            self.code = None

    def generate(self, fp):
        logger.info('TaskSerial: name={}'.format(self.name))
        if self.code is not None:
            fp.write(self.code)

class TaskParallel:
    def __init__(self, name, info, platform):
        self.name = name
        self.info = info
        self.platform = platform

        self.prev_log_file = None
        self.setup(info)
        pass

    def setup(self, info):
        node = info.get('node', [1,1,1])
        if type(node) is list:
            node = (node + [1,1,1])[0:3]
        elif type(node) is dict:
            msg = 'node must be scalar or list'
            logger.error(msg)
            raise ValueError(msg)
        else:
            node = [node, 1, 1]
        self.node = node

        self.func_name = 'task_{}'.format(self.name)
        self.log_file = 'log_{}.dat'.format(self.name)
        self.prev_log_file = info.get('prev_log_file', None)

        self.code = info.get('run', '')

        self.resume = 'resume'
        pass

    def generate(self, fp):
        logger.info('TaskParallel: name={}'.format(self.name))

        srun_str = self.platform.parallel_command({'node': self.node})

        run = self.code
        run = re.sub(r'\n$','', run)
        run = re.sub(r'(srun|mpirun|mpiexec)', srun_str, run)
        run = re.sub(r'^',r'  ', run)
        run = re.sub(r'\n',r'\n  ', run)

        func_lines = []
        func_lines.append(('function {} ()'.format(self.func_name)) + ' {')
        func_lines.append('  set -e')
        func_lines.append('  _work_item=$1')
        func_lines.append('  _slot_id=$2')
        func_lines.append('  _workdir=$_work_item')
        if self.prev_log_file is not None:
            func_lines.append('  if ! is_ready_ $_work_item {}; then'.format(self.prev_log_file))
            func_lines.append('    exit -1')
            func_lines.append('  fi')
        func_lines.append('  cd $_workdir')
        func_lines.append(run)
        func_lines.append('}')
        func_lines.append('export -f {}\n'.format(self.func_name))

        if self.resume == 'resume':
            resume_opt = '--resume'
        elif self.resume == 'retry':
            resume_opt = '--resume-failed'
        else:
            resume_opt = ''
        
        parallel_opt = '-j `find_multiplicity_ {}` --jl {} {}'.format(self.node[0], self.log_file, resume_opt)
        exec_lines = []
        exec_lines.append('date')
        exec_lines.append('echo "  {}"'.format(self.name))
        exec_lines.append('cat $@ | parallel {} {} {{}} {{%}}'.format(parallel_opt, self.func_name))

        fp.write('\n'.join(func_lines) + '\n')
        fp.write('\n'.join(exec_lines) + '\n')
        fp.write('\n')

class ScriptGenerator:
    func_def = r"""
function is_ready_ () {
    item_=$1
    logfile_=$2
    if [ ! -e $logfile_ ]; then
        return 1
    fi
    status=`grep '\b'$item_'\b' $logfile_ | tail -1 | awk '{print $7}'`
    if [ -z "$status" ]; then
        return 1
    fi
    if [ $status = 0 ]; then
        return 0
    else
        return 1
    fi
}
export -f is_ready_

function find_multiplicity_ () {
    nnodes=$1
    nmult=$(( SLURM_NNODES / nnodes ))
    echo $nmult
}
export -f find_multiplicity_

"""

    def __init__(self, info):
        self.info = info
        self.setup(info)

    def setup(self, info):
        self.name = info.get('name', sys.argv[0])
        self.desc = info.get('description', None)

        self.platform = Platform.create(info.get('platform', None))
        if self.platform.job_name is None:
            self.platform.job_name = self.name

        prologue = TaskSerial('prologue', info.get('prologue', None), self.platform)
        epilogue = TaskSerial('epilogue', info.get('epilogue', None), self.platform)

        func_def = TaskSerial('function_definitions', { 'code': self.func_def }, self.platform)

        self.tasklist = []
        prev_log_file = None

        jobs = info.get('jobs', {})
        for task_name, task_info in jobs.items():
            task_type = task_info.get('parallel', True)
            if task_type:
                task_info.update({'prev_log_file': prev_log_file})
                task = TaskParallel(task_name, task_info, self.platform)
                prev_log_file = task.log_file
            else:
                task = TaskSerial(task_name, task_info, self.platform)
            self.tasklist.append(task)

        self.tasklist.insert(0, prologue)
        self.tasklist.insert(1, func_def)
        self.tasklist.append(epilogue)
    
    def generate(self, fp):
        self.platform.generate_header(fp)
        for task in self.tasklist:
            task.generate(fp)
        pass

def run(*, info_file = None, info_dict = None):
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
    scriptgen.generate(sys.stdout)

def main():
    import argparse

    parser = argparse.ArgumentParser(prog='moller')
    parser.add_argument('input_yaml', nargs='?', default=None, help='task description file')
    parser.add_argument('--version', action='atore_true', help='show version')

    args = parser.parse_args()

    if args.version:
        print('moller', moller.__version__)
        sys.exit(0)

    if args.input_yaml is None:
        parser.print_help()
        sys.exit(1)

    run(input_file = args.input_yaml)

if __name__ == '__main__':
    args = sys.argv
    if len(args) >=2 :
        # try:
        #     run(info_file = args[1])
        # except Exception as e:
        #     logger.error(e)
        #     sys.exit(1)
        run(info_file = args[1])    

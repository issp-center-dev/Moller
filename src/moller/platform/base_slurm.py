from .base import Platform
from .function import ScriptFunction
from .utils import *

import logging
logger = logging.getLogger(__name__)

class BaseSlurm(Platform):
    def __init__(self, info):
        super().__init__(info)
        self.setup(info)

    def setup(self, info):
        super().batch_queue_setup(info)

    def parallel_command(self, info):
        #--- system dependent
        exec_command=r'srun --exclusive -N $_nn -n $_np -c $_nc'
        
        node = info.get('node', None)
        #cmd = exec_command + (r'-N {} -n {} -c {}'.format(*node))
        cmd = exec_command
        return cmd

    def generate_header(self, fp):
        shebang = '#!/bin/bash\n'

        sched_key = '#SBATCH '

        sched_params = []
        sched_params.append(self.generate_queue_line())
        sched_params.append(self.generate_node_line())
        sched_params.append(self.generate_elapsed_line())
        sched_params.append(self.generate_jobname_line())

        if "options" in self.info and self.info["options"] is not None:
            opt = self.info["options"]
            if type(opt) == str:
                sched_params += [t.strip() for t in opt.splitlines() if len(t.strip()) > 0]
            elif type(opt) == list:
                sched_params += opt
            else:
                logger.error("unknown option type {}".type(opt))
                raise ValueError("unknown option type {}".type(opt))

        fp.write(shebang)
        fp.write('\n'.join([ sched_key + s for s in sched_params if s is not None ]) + '\n\n')
        fp.write(self.generate_header_append())

    def generate_queue_line(self):
        return "-p {}".format(self.queue) if self.queue else None

    def generate_elapsed_line(self):
        return "-t {}".format(convert_seconds_to_hhmmss(self.elapsed)) if self.elapsed else None

    def generate_jobname_line(self):
        return "-J {}".format(self.job_name) if self.job_name else None

    def generate_node_line(self):
        return "-N {}".format(self.nnode) if self.nnode else None

    function_find_multiplicity = r"""
function _find_multiplicity () {
    _sig=$1
    _s=(${_sig//,/ })
    _nn=${_s[0]}
    _np=${_s[1]}
    _nc=${_s[2]}
    if [ $_nn = 0 ]; then
        if [ $_ncores -lt $_nc ]; then
            echo "ERROR: cpus_per_task exceeds cpus on node" >&2
            exit 1
        fi
        _p=$(( _ncores / _nc ))
        if [ $_p -gt $_np ]; then
            _q=$(( _p / _np ))
            _w=$(( _nnodes * _q ))
	    _s="1,$_np,$_nc"
	    DEBUG "multiplicity: pack into single node: $_q procs, $_w tasks"
        else
            _r=$(( _np % _p == 0 ?  _np / _p : _np / _p + 1 ))
            _w=$(( _nnodes / _r ))
	    _s="$_r,$_np,$_nc"
	    DEBUG "multiplicity: requires $_r nodes. $_w tasks"
        fi
    else
        _v1=$(( _np * _nc ))
        _v2=$(( _nn * _ncores ))
        if [ $_v1 -gt $_v2 ]; then
            echo "ERROR: number of cpus exceed total allocation" >&2
            exit 1
        fi
        _w=$(( _nnodes / _nn ))
	_s=$_sig
	DEBUG "multiplicity: nodes specified. $_w tasks"
    fi
    _multiplicity=$_w
    _signature=$_s
    DEBUG "multiplicity: mult=$_multiplicity, sig=$_signature"
}
    """

    function_setup_taskenv = r"""
function _setup_taskenv () {
    :
}
export -f _setup_taskenv
    """

    function_setup_run_parallel = r"""
function _setup_run_parallel () {
    _parallel_opt=""
}
export -f _setup_run_parallel
    """

    def generate_function_body(self):
        flist = ScriptFunction.function_defs
        flist.append(self.function_find_multiplicity)
        flist.append(self.function_setup_taskenv)
        flist.append(self.function_setup_run_parallel)
        return ''.join(flist)
        
    def generate_variable(self):
        var_list = []
        var_list.append(r'_nnodes=$SLURM_NNODES')
        var_list.append(r'_ncores=$SLURM_CPUS_ON_NODE')
        var_list.append(r'_multiplicity=0')
        var_list.append(r'_signature=""')
        return '\n'.join(var_list) + '\n'

    def generate_function(self):
        str = ''
        str += ScriptFunction.function_setup_vars
        str += self.generate_variable()
        str += self.generate_function_body()
        str += ScriptFunction.function_main
        return str

    def generate_header_append(self):
        str = ''
        str += 'export _debug=0\n'
        str += ScriptFunction.function_main_pre + '\n'
        return str
        
    @classmethod
    def create(cls, info):
        return cls(info)

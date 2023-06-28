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
        sched_params.append('-p {}'.format(self.queue))
        sched_params.append('-N {}'.format(self.nnode))
        sched_params.append('-t {}'.format(convert_seconds_to_hhmmss(self.elapsed)))
        if self.job_name is not None:
            sched_params.append('-J {}'.format(self.job_name))

        fp.write(shebang)
        fp.write('\n'.join([ sched_key + s for s in sched_params ]) + '\n')
        fp.write('\n')
        fp.write('export _debug=1')
        fp.write('\n')

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
	    [ $_debug -eq 1 ] && echo "DEBUG: multiplicity: pack into single node: $_q procs, $_w tasks"
        else
            _r=$(( _np % _p == 0 ?  _np / _p : _np / _p + 1 ))
            _w=$(( _nnodes / _r ))
	    _s="$_r,$_np,$_nc"
	    [ $_debug -eq 1 ] && echo "DEBUG: multiplicity: requires $_r nodes. $_w tasks"
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
	[ $_debug -eq 1 ] && echo "DEBUG: multiplicity: nodes specified. $_w tasks"
    fi
    _multiplicity=$_w
    _signature=$_s
    [ $_debug -eq 1 ] && echo "DEBUG: multiplicity: mult=$_multiplicity, sig=$_signature"
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
        var_list.append(r'_resume_opt="--resume"')
        return '\n'.join(var_list) + '\n'

    def generate_function(self):
        str  = self.generate_variable()
        str += self.generate_function_body()
        str += ScriptFunction.function_main
        return str
        
    @classmethod
    def create(cls, info):
        return cls(info)


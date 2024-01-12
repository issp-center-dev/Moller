from .base import Platform
from .function import ScriptFunction
from .utils import *

import logging
logger = logging.getLogger(__name__)

class BaseDefault(Platform):
    def __init__(self, info):
        super().__init__(info)
        self.setup(info)

    def setup(self, info):
        pass

    def parallel_command(self, info):
        return ""

    def generate_header(self, fp):
        shebang = '#!/bin/bash\n'
        fp.write(shebang)
        fp.write('\n')
        fp.write(self.generate_header_append())

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

    function_main_pre = r"""
_initargs="$@"
"""

    function_main = r"""
#--- initialize
_setup_max_njob

#--- parse options
scriptargs=""
retry=0

function argparse () {
    while [ -n "$*" ]
    do
        case "$1" in
            -h | --help | -help)
                echo $0 [--retry] listfile [...]
                exit 0
                ;;
            --retry | -retry)
                retry=1
                shift
                ;;
            --node | -node)
                _nnodes=$2
                shift
                shift
                ;;
            --core | -core)
                _ncores=$2
                shift
                shift
                ;;
            --)
                shift
                break
                ;;
            -*)
                echo "unknown option: $1"
                exit 1
                ;;
            *)
                scriptargs="$scriptargs $1"
                shift
                ;;
        esac
    done
}

argparse $_initargs

if [ $_nnodes -eq 0 ]; then
    _nnodes=1
fi

if [ $_ncores -eq 0 ]; then
    _ncores=`nproc`
fi

DEBUG "nnodes=$_nnodes, ncores=$_ncores"

if [ -z $scriptargs ]; then
    #echo "no listfile specified"
    #exit 0
    if [ -e "list.dat" ]; then
	echo "no listfile specified. assume default: list.dat"
	scriptargs="list.dat"
    else
	echo "no listfile specified. stop."
	exit 0
    fi
fi

_resume_opt="--resume"
if [ $retry -gt 0 ]; then
    echo "INFO: retry enabled"
    _resume_opt="--resume-failed"
fi

mplist=( `cat $scriptargs | xargs` )
"""

    def generate_function_body(self):
        flist = ScriptFunction.function_defs
        flist.append(self.function_find_multiplicity)
        flist.append(self.function_setup_taskenv)
        flist.append(self.function_setup_run_parallel)
        return ''.join(flist)

    def generate_variable(self):
        var_list = []
        var_list.append(r'_nnodes={}'.format(self.nnode))
        var_list.append(r'_ncores={}'.format(self.ncore))
        var_list.append(r'_multiplicity=0')
        var_list.append(r'_signature=""')
        return '\n'.join(var_list) + '\n'

    def generate_function(self):
        str = ''
        str += ScriptFunction.function_setup_vars
        str += self.generate_variable()
        str += self.generate_function_body()
        str += self.function_main
        return str

    def generate_header_append(self):
        str = ''
        str += 'export _debug=0\n'
        str += self.function_main_pre
        return str

    @classmethod
    def create(cls, info):
        return cls(info)

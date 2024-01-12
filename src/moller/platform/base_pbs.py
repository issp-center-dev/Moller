from .base import Platform
from .function import ScriptFunction
from .utils import *

import logging
logger = logging.getLogger(__name__)

class BasePBS(Platform):
    def __init__(self, info):
        super().__init__(info)
        self.setup(info)
        self.pbs_use_old_format = False

    def setup(self, info):
        super().batch_queue_setup(info)

    def parallel_command(self, info):
        #--- system dependent
        exec_command=r'mpirun -np $_np -hosts $_node -ppn $_ppn -genvall'
        
        node = info.get('node', None)
        #cmd = exec_command + (r'-N {} -n {} -c {}'.format(*node))
        cmd = exec_command
        return cmd

    def generate_header(self, fp):
        shebang = '#!/bin/bash\n'

        sched_key = '#PBS '

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
        return "-q {}".format(self.queue) if self.queue else None

    def generate_node_line(self):
        if self.pbs_use_old_format:
            if self.nnode is None:
                return None
            if self.ncore is not None:
                return '-l nodes={}:ppn={}'.format(self.nnode, self.ncore)
            else:
                return '-l nodes={}'.format(self.nnode)
        else:
            if self.nnode is None:
                return None
            if self.ncore is not None:
                return '-l select={}:ncpus={}'.format(self.nnode, self.ncore)
            else:
                return '-l select={}'.format(self.nnode)

    def generate_elapsed_line(self):
        return "-l walltime={}".format(convert_seconds_to_hhmmss(self.elapsed)) if self.elapsed else None

    def generate_jobname_line(self):
        return "-N {}".format(self.job_name) if self.job_name else None

    function_find_multiplicity = r"""
function _gen_mask () {
    _n=$1
    _m=${2:-0}
    _s=''
    _ma=$(( _m / 4 ))
    _mb=$(( _m % 4 ))
    for (( _i=0; _i<_ma; ++_i )); do
	_s="0$_s"
    done
    if [ $_mb -gt 0 ]; then
	_mc=$(( 4 - _mb ))
	_md=$(( _mc < _n ? _mc : _n ))
	_x=`printf "%x" $(( ((1<<$_md)-1) << _mb ))`
	_s="$_x$_s"
	_n=$(( _n - _md ))
    fi
    _ms=$(( _n / 4 ))
    _mt=$(( _n % 4 ))
    for (( _i=0; _i<_ms; ++_i )); do
	_s="f$_s"
    done
    if [ $_mt -gt 0 ]; then
	_x=`printf "%x" $(( (1<<$_mt)-1 ))`
	_s="$_x$_s"
    fi
    _s="0x$_s"
    echo $_s
}

function _find_multiplicity () {
    _sig=$1
    _ss=(${_sig//,/ })
    _nn=${_ss[0]}
    _np=${_ss[1]}
    _nc=${_ss[2]}

    _node_table=("none")
    _mask_table=("none")
    
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

	    for (( _j=0; _j<_w; ++_j )); do
		_a=$(( _j % _nnodes ))
		_b=$(( _j / _nnodes ))
		_node_table+=(${_nodes[$_a]})
	    done

	    if [ $_enable_mask -eq 1 ]; then
		declare -a _mask_pat=()
		for (( _i=0; _i<_p; ++_i )); do
		    _offset=$(( _nc * _i ))
		    _x=`_gen_mask $_nc $_offset`
		    _mask_pat+=($_x)
		done
		for (( _j=0; _j<_w; ++_j )); do
		    _a=$(( _j % _nnodes ))
		    _b=$(( _j / _nnodes ))
		    _idx=$(( _np * _b ))
		    _md="${_mask_pat[$_idx]}"
		    for (( _i=1; _i<_np; ++_i )); do
			_idx=$(( _idx + 1 ))
			_md="$_md,${_mask_pat[$_idx]}"
		    done
		    _mask_table+=($_md)
		done
	    fi
	else
	    _r=$(( _np % _p == 0 ?  _np / _p : _np / _p + 1 ))
	    _w=$(( _nnodes / _r ))
	    _s="$_r,$_np,$_nc"

	    _k=0
	    for (( _j=0; _j<_w; ++_j )); do
		_nd=${_nodes[$_k]}
		_k=$(( _k + 1 ))
		for (( _i=1; _i<_r; ++_i )); do
		    _nd="$_nd,${_nodes[$_k]}"
		    _k=$(( _k + 1 ))
		done
		_node_table+=($_nd)
	    done
	fi
    else
	_v1=$(( _np * _nc ))
	_v2=$(( _nn * _ncores ))
	if [ $_nn -gt $_nnodes -o $_v1 -gt $_v2 ]; then
	    echo "ERROR: number of cpus exceed total allocation" >&2
	    exit 1
	fi
	_w=$(( _nnodes / _nn ))
	_s=$_sig
	_k=0
	for (( j=0; j<_w; ++j )); do
	    _nd=${_nodes[$_k]}
	    _k=$(( _k + 1 ))
	    for (( i=1; i<_nn; ++i )); do
		_nd="$_nd,${_nodes[$_k]}"
		_k=$(( _k + 1 ))
	    done
	    _node_table+=($_nd)
	done
    fi
    _multiplicity=$_w
    _signature=$_s

    # check
    if [ ${_multiplicity} -lt 1 ]; then
        echo "ERROR: insufficient number of allocated cores"
        exit 1
    fi
}
    """

    function_setup_taskenv = r"""
function _setup_taskenv () {
  eval $_pack_node_table
  eval $_pack_mask_table
  _node=${_node_table[$_slot_id]}
  if [ ${#_mask_table[@]} -le 1 ]; then
      _mask=$_ncores
  else
      _mask="[${_mask_table[$_slot_id]}]"
  fi

  _ppn=$(( _np % _nn == 0 ? _np/_nn : _np/_nn + 1 ))
  
  export OMP_NUM_THREADS=$_nc
  export I_MPI_PIN_DOMAIN=$_mask
  DEBUG "$_work_item: host=$_node mask=$_mask nthr=$_nc"
}
export -f _setup_taskenv
    """

    function_setup_run_parallel = r"""
function _setup_run_parallel () {
    export _pack_node_table=`declare -p _node_table`
    export _pack_mask_table=`declare -p _mask_table`
    _parallel_opt="--env _pack_node_table --env _pack_mask_table"
}
export -f _setup_run_parallel
    """

    function_setup_variables = r"""
declare -a _nodes=( `cat $PBS_NODEFILE | sort | uniq | xargs` )
_nnodes=${#_nodes[@]}

_ncores=0
if [ -n "${NCPUS+x}" ]; then
    _ncores=${NCPUS}
elif [ -n "${OMP_NUM_THREADS+x}" ]; then
    _ncores=${OMP_NUM_THREADS}
elif [ -n "${moller_core}" ]; then
    _ncores=${moller_core}
else
    _nc=`cat $0 | grep '^#PBS' | egrep '(ppn|ncpus)=' | sed -e 's/.*\(ppn\|ncpus\)=\([0-9]*\).*/\2/'`
    if [ -n "${_nc}" ]; then
            _ncores=$_nc
    else
        echo "ERROR: cannot find number of cores per node"
        exit 1
    fi
fi
export _ncores

_multiplicity=0
declare -a _node_table=()
declare -a _mask_table=()
_signature=""

if [ $_debug -gt 0 ]; then
    echo "DEBUG: nodefile=$PBS_NODEFILE"
    echo "DEBUG: nodes=${_nodes[@]}"
    echo "DEBUG: cores=$_ncores"
fi
"""

    def generate_function_body(self):
        flist = ScriptFunction.function_defs
        flist.append(self.function_find_multiplicity)
        flist.append(self.function_setup_taskenv)
        flist.append(self.function_setup_run_parallel)
        return ''.join(flist)
        
    def generate_variable(self):
        str = ""

        var_list = []
        var_list.append(r'export _enable_mask=0')
        str += '\n'.join(var_list) + '\n'

        str += "\n"
        str += "moller_node={}".format(self.nnode if self.nnode else "") + "\n"
        str += "moller_core={}".format(self.ncore if self.ncore else "") + "\n"

        str += self.function_setup_variables
        #str += "_setup_variables\n"

        return str

    def generate_function(self):
        str = ''
        str += ScriptFunction.function_setup_vars
        str += self.generate_variable()
        str += self.generate_function_body()
        str += ScriptFunction.function_main_noargs
        return str

    def generate_header_append(self):
        str = ''
        str += 'export _debug=0\n\n'
        str += 'cd $PBS_O_WORKDIR\n\n'
        return str
        
    @classmethod
    def create(cls, info):
        return cls(info)

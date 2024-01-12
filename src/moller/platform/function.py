import logging
logger = logging.getLogger(__name__)

class ScriptFunction:
    def __init__(self, info):
        pass

    function_setup_vars = r"""
"""

    function_debug = r"""
function DEBUG () {
    if [ $_debug -gt 0 ]; then
        echo "DEBUG:" $@
    fi
}
export -f DEBUG
"""

    function_is_ready = r"""
function _is_ready () {
    item_=$1
    logfile_=$2
    if [ ! -e $logfile_ ]; then
        l_=`ls ${logfile_}.[0-9]* 2> /dev/null`
        if [ -z "$l_" ]; then
            DEBUG "$item_: logfile $logfile_ not found"
            return 1
        fi
        logfile_=${l_}
    fi
    status=`grep -h '\s'$item_'\s' $logfile_ | tail -1 | awk '{print $7}'`
    if [ -z "$status" ]; then
	DEBUG "$item_: status not found"
        return 1
    fi
    if [ $status = 0 ]; then
	DEBUG "$item_: status ok. lets proceed"
        return 0
    else
	DEBUG "$item_: status not ready"
        return 1
    fi
}
export -f _is_ready
    """

    function_setup_max_njob = r"""
_max_njob=1024

function _setup_max_njob () {
    _req_openfiles=16384
    _num_openfiles=`ulimit -n`
    _limit_openfiles=`ulimit -Hn`
    if [ $_num_openfiles -ge $_req_openfiles ]; then
        :
	DEBUG "setup_max_njob: num_openfiles already satisfied"
    elif [ $_req_openfiles -le $_limit_openfiles ]; then
        ulimit -n $_req_openfiles
	DEBUG "setup_max_njob: num_openfiles set to $_req_openfiles"
    else
        ulimit -n $_limit_openfiles
	DEBUG "setup_max_njob: num_openfiles set to upper limit $_limit_openfiles"
    fi
    _num_openfiles=`ulimit -n`
    _limit_njob=$(( ((_num_openfiles - 16) / 4) /10*9 ))
    if [ $_max_njob -gt $_limit_njob ]; then
        _max_njob=$_limit_njob
    fi
    DEBUG "max_njob=$_max_njob"
}
    """

    function_run_parallel = r"""
function _run_parallel_task () {
    _cmd=$1
    _sig=$2
    _arg=$3
    _x0=$4
    _w0=$5
    _x1=$6
    _slot_id=$(( 1+(_x1-1)+_w0*(_x0-1) ))
    DEBUG "run task: $_cmd $_arg $_sig x0=$_x0, w0=$_w0, x1=$_x1, slot=$_slot_id"
    $_cmd $_sig $_arg $_slot_id
}
export -f _run_parallel_task

function run_parallel () {
    #_njob=$1
    _sig=$1
    _cmd=$2
    _logfile=$3

    _find_multiplicity $_sig
    _njob=$_multiplicity
    _sig2=$_signature

    _setup_run_parallel

    if [ $_njob -le $_max_njob ]; then
	DEBUG "run: cmd=$_cmd, log=$_logfile, sig=$_sig2, njob=$_njob, resume=$_resume_opt"
        parallel $_resume_opt --joblog ${_logfile} -j $_njob $_cmd "$_sig2" {} {%}
    else
        _k=0
        while /bin/true
        do
            _t=$(( 4**_k ))
            if [ $_njob -le $_t ]; then
                break
            fi
            _k=$(( _k + 1 ))
        done
        _nchunk=$(( 2**_k ))
        _nway=$(( _njob % _nchunk == 0 ? _njob / _nchunk : _njob / _nchunk + 1 ))
        DEBUG "run nested: nchunk=${_nchunk}, nway=${_nway}, cmd=$_cmd, log=$_logfile, sig=$_sig2, resume=$_resume_opt"
        parallel --pipe --roundrobin -N $_nchunk -j $_nway --slotreplace '{X0}' \
             parallel -j $_nchunk \
                 $_resume_opt --joblog ${_logfile}.{X0} \
                 -I '{W}' --slotreplace '{X1}' \
                 _run_parallel_task $_cmd "$_sig2" {W} {X0} $_nchunk {X1}
    fi
}
export -f run_parallel
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

    function_main_noargs_pre = r"""
#--- parameters
retry=0
scriptargs="list.dat"
"""

    function_main_noargs = r"""
#--- initialize
_setup_max_njob

_resume_opt="--resume"
if [ $retry -gt 0 ]; then
    echo "INFO: retry enabled"
    _resume_opt="--resume-failed"
fi

mplist=( `cat $scriptargs | xargs` )
"""

    function_defs = [
        function_debug,
        function_is_ready,
        function_setup_max_njob,
        function_run_parallel,
    ]

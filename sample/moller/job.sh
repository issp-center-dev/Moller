#!/bin/bash
#SBATCH -p i8cpu
#SBATCH -N 8
#SBATCH -t 0:30:00
#SBATCH -J testjob

export _debug=1
module purge
module load oneapi_compiler/2023.0.0 openmpi/4.1.5-oneapi-2023.0.0-classic

ulimit -s unlimited

source /home/issp/materiapps/intel/parallel/parallelvars-20210622-1.sh
source /home/issp/materiapps/oneapi_compiler_classic-2023.0.0--openmpi-4.1.5/espresso/espressovars-7.2-1.sh

source ~/misc/miniconda3/env.sh
conda activate py39-moller

#PATH_W90="/home/i0016/i001600/program/q-e6.6/bin"
export PATH_TOML=$(pwd)
export cif2qewan="/home/i0018/i001800/tools/moller/tools/cif2qewan.git/cif2qewan.py"
export CIF2QEWAN_DIR="/home/i0018/i001800/tools/moller/tools/cif2qewan.git"

# Option to use dual rail
#export MPI_IB_RAILS=2

#MKL_DEBUG_CPU_TYPE=5
ulimit -s unlimited
export KMP_STACKSIZE=512m
export UCX_TLS='self,sm,ud'
_nnodes=$SLURM_NNODES
_ncores=$SLURM_CPUS_ON_NODE
_multiplicity=0
_signature=""
_resume_opt="--resume"

function _is_ready () {
    item_=$1
    logfile_=$2
    if [ ! -e $logfile_ ]; then
	[ $_debug -eq 1 ] && echo "DEBUG: $item_: logfile $logfile_ not found"
        return 1
    fi
    status=`grep '\b'$item_'\b' $logfile_ | tail -1 | awk '{print $7}'`
    if [ -z "$status" ]; then
	[ $_debug -eq 1 ] && echo "DEBUG: $item_: status not found"
        return 1
    fi
    if [ $status = 0 ]; then
	[ $_debug -eq 1 ] && echo "DEBUG: $item_: status ok. lets proceed"
        return 0
    else
	[ $_debug -eq 1 ] && echo "DEBUG: $item_: status not ready"
        return 1
    fi
}
export -f _is_ready
    
_max_njob=1024

function _setup_max_njob () {
    _req_openfiles=16384
    _num_openfiles=`ulimit -n`
    _limit_openfiles=`ulimit -Hn`
    if [ $_num_openfiles -ge $_req_openfiles ]; then
        :
	[ $_debug -eq 1 ] && echo "DEBUG: setup_max_njob: num_openfiles already satisfied"
    elif [ $_req_openfiles -le $_limit_openfiles ]; then
        ulimit -n $_req_openfiles
	[ $_debug -eq 1 ] && echo "DEBUG: setup_max_njob: num_openfiles set to $_req_openfiles"
    else
        ulimit -n $_limit_openfiles
	[ $_debug -eq 1 ] && echo "DEBUG: setup_max_njob: num_openfiles set to upper limit $_limit_openfiles"
    fi
    _num_openfiles=`ulimit -n`
    _limit_njob=$(( ((_num_openfiles - 16) / 4) /10*9 ))
    if [ $_max_njob -gt $_limit_njob ]; then
        _max_njob=$_limit_njob
    fi
    [ $_debug -eq 1 ] && echo "DEBUG: max_njob=$_max_njob"
}
    
function _run_parallel_task () {
    _cmd=$1
    _sig=$2
    _arg=$3
    _x0=$4
    _w0=$5
    _x1=$6
    _slot_id=$(( 1+(_x1-1)+_w0*(_x0-1) ))
    [ $_debug -eq 1 ] && echo "DEBUG: run task: $_cmd $_arg $_sig x0=$_x0, w0=$_w0, x1=$_x1, slot=$_slot_id"
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
	[ $_debug -eq 1 ] && echo "DEBUG: run: cmd=$_cmd, log=$_logfile, sig=$_sig2, njob=$_njob, resume=$_resume_opt"
        parallel $_resume_opt --joblog ${_logfile} -j $_njob $_cmd "$_sig2" {} {%}
    else
        _min_nchunk=16
        _nchunk=$(( _min_nchunk < _njob/_max_njob ? _njob/_max_njob : _min_nchunk ))
        _nway=$(( _njob % _nchunk == 0 ? _njob / _nchunk : _njob / _nchunk + 1 ))
        [ $_debug -eq 1 ] && echo "DEBUG: run nested: nchunk=${_nchunk}, nway=${_nway}, cmd=$_cmd, log=$_logfile, sig=$_sig2, resume=$_resume_opt"
        parallel --pipe --roundrobin -N $_nchunk -j $_nway --slotreplace '{X0}' \
             parallel -j $_nchunk \
                 $_resume_opt --joblog ${_logfile}.{X0} \
                 -I '{W}' --slotreplace '{X1}' \
                 _run_parallel_task $_cmd "$_sig2" {W} {X0} $_nchunk {X1}
    fi
}
export -f run_parallel
    
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
    
function _setup_taskenv () {
    :
}
export -f _setup_taskenv
    
function _setup_run_parallel () {
    _parallel_opt=""
}
export -f _setup_run_parallel
        
#--- initialize
_setup_max_njob

#--- parse options
initargs="$@"
scriptargs=""
retry=0

while [ -n "$*" ]
do
    case "$1" in
	-h | --help | -help)
	    echo $0 [--retry] listfile [...]
	    exit 0
	    ;;
	--retry | -retry)
	    _resume_opt="--resume-failed"
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

mplist=( `cat $scriptargs | xargs` )
echo "start..."
function task_cif2qe () {
  set -e
  _sig=$1
  _work_item=$2
  _slot_id=$3
  _workdir=$_work_item

  _s=(${_sig//,/ })
  _nn=${_s[0]}
  _np=${_s[1]}
  _nc=${_s[2]}

  _setup_taskenv

  cd $_workdir

  if [ -d qe ]; then
    if [ -d qe_old ]; then
      echo "qe_old dir exists in $_workdir. remove qe_old"
      rm -rf qe_old
    fi
    echo "qe dir exists in $_workdir. mv qe qe_old"
    mv qe qe_old
  fi
  mkdir qe
  cp *.cif qe
  cd qe
  [ $_debug -eq 1 ] && echo "DEBUG: $_work_item: srun --exclusive --mem-per-cpu=1840 -N $_nn -n $_np -c $_nc python3 ${cif2qewan} *.cif ${PATH_TOML}/cif2qewan.toml"
  srun --exclusive --mem-per-cpu=1840 -N $_nn -n $_np -c $_nc python3 ${cif2qewan} *.cif ${PATH_TOML}/cif2qewan.toml
}
export -f task_cif2qe

date
echo "  cif2qe"
printf '%s\n' ${mplist[@]} | run_parallel 1,1,1 task_cif2qe log_cif2qe.dat

function task_scf () {
  set -e
  _sig=$1
  _work_item=$2
  _slot_id=$3
  _workdir=$_work_item

  _s=(${_sig//,/ })
  _nn=${_s[0]}
  _np=${_s[1]}
  _nc=${_s[2]}

  _setup_taskenv

  if ! _is_ready $_work_item log_cif2qe.dat; then
    exit -1
  fi
  cd $_workdir

  cd qe
  [ $_debug -eq 1 ] && echo "DEBUG: $_work_item: srun --exclusive --mem-per-cpu=1840 -N $_nn -n $_np -c $_nc pw.x -nk 24 -in scf.in > scf.out"
  srun --exclusive --mem-per-cpu=1840 -N $_nn -n $_np -c $_nc pw.x -nk 24 -in scf.in > scf.out
}
export -f task_scf

date
echo "  scf"
printf '%s\n' ${mplist[@]} | run_parallel 0,24,4 task_scf log_scf.dat

function task_copy_work () {
  set -e
  _sig=$1
  _work_item=$2
  _slot_id=$3
  _workdir=$_work_item

  _s=(${_sig//,/ })
  _nn=${_s[0]}
  _np=${_s[1]}
  _nc=${_s[2]}

  _setup_taskenv

  if ! _is_ready $_work_item log_scf.dat; then
    exit -1
  fi
  cd $_workdir

  cd qe
  cp -r work check_wannier
  cp -r work band
}
export -f task_copy_work

date
echo "  copy_work"
printf '%s\n' ${mplist[@]} | run_parallel 1,1,1 task_copy_work log_copy_work.dat

function task_nscf () {
  set -e
  _sig=$1
  _work_item=$2
  _slot_id=$3
  _workdir=$_work_item

  _s=(${_sig//,/ })
  _nn=${_s[0]}
  _np=${_s[1]}
  _nc=${_s[2]}

  _setup_taskenv

  if ! _is_ready $_work_item log_copy_work.dat; then
    exit -1
  fi
  cd $_workdir

  cd qe/check_wannier
  sed -e "s/electrons/electrons\n  diagonalization = 'cg'/g" nscf.in > nscf_cg.in
  [ $_debug -eq 1 ] && echo "DEBUG: $_work_item: srun --exclusive --mem-per-cpu=1840 -N $_nn -n $_np -c $_nc pw.x -nk 64 -in nscf_cg.in > nscf.out"
  srun --exclusive --mem-per-cpu=1840 -N $_nn -n $_np -c $_nc pw.x -nk 64 -in nscf_cg.in > nscf.out
}
export -f task_nscf

date
echo "  nscf"
printf '%s\n' ${mplist[@]} | run_parallel 0,64,2 task_nscf log_nscf.dat

function task_band () {
  set -e
  _sig=$1
  _work_item=$2
  _slot_id=$3
  _workdir=$_work_item

  _s=(${_sig//,/ })
  _nn=${_s[0]}
  _np=${_s[1]}
  _nc=${_s[2]}

  _setup_taskenv

  if ! _is_ready $_work_item log_nscf.dat; then
    exit -1
  fi
  cd $_workdir

  cd qe/band
  sed -e "s/electrons/electrons\n  diagonalization = 'cg'/g" nscf.in > nscf_cg.in
  [ $_debug -eq 1 ] && echo "DEBUG: $_work_item: srun --exclusive --mem-per-cpu=1840 -N $_nn -n $_np -c $_nc pw.x -nk 64 -in nscf_cg.in > nscf.out"
  srun --exclusive --mem-per-cpu=1840 -N $_nn -n $_np -c $_nc pw.x -nk 64 -in nscf_cg.in > nscf.out
  [ $_debug -eq 1 ] && echo "DEBUG: $_work_item: srun --exclusive --mem-per-cpu=1840 -N $_nn -n $_np -c $_nc bands.x -nk 64 -in band.in > band.out"
  srun --exclusive --mem-per-cpu=1840 -N $_nn -n $_np -c $_nc bands.x -nk 64 -in band.in > band.out
}
export -f task_band

date
echo "  band"
printf '%s\n' ${mplist[@]} | run_parallel 0,64,2 task_band log_band.dat

function task_nscf2 () {
  set -e
  _sig=$1
  _work_item=$2
  _slot_id=$3
  _workdir=$_work_item

  _s=(${_sig//,/ })
  _nn=${_s[0]}
  _np=${_s[1]}
  _nc=${_s[2]}

  _setup_taskenv

  if ! _is_ready $_work_item log_band.dat; then
    exit -1
  fi
  cd $_workdir

  cd qe
  sed -e "s/electrons/electrons\n  diagonalization = 'cg'/g" nscf.in > nscf_cg.in
  [ $_debug -eq 1 ] && echo "DEBUG: $_work_item: srun --exclusive --mem-per-cpu=1840 -N $_nn -n $_np -c $_nc pw.x -nk 64 -in nscf_cg.in > nscf_cg.out"
  srun --exclusive --mem-per-cpu=1840 -N $_nn -n $_np -c $_nc pw.x -nk 64 -in nscf_cg.in > nscf_cg.out
}
export -f task_nscf2

date
echo "  nscf2"
printf '%s\n' ${mplist[@]} | run_parallel 0,64,2 task_nscf2 log_nscf2.dat

echo "done."

#!/bin/bash
#SBATCH -p i8cpu
#SBATCH -N 8
#SBATCH -t 0:30:00
#SBATCH -J testjob

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

echo "start..."
function task_cif2qe () {
  set -e
  _work_item=$1
  _slot_id=$2
  _workdir=$_work_item
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
  srun --exclusive -N 1 -n 1 -c 1 python3 ${cif2qewan} *.cif ${PATH_TOML}/cif2qewan.toml
}
export -f task_cif2qe

date
echo "  cif2qe"
cat $@ | parallel -j `find_multiplicity_ 1` --jl log_cif2qe.dat --resume task_cif2qe {} {%}

function task_scf () {
  set -e
  _work_item=$1
  _slot_id=$2
  _workdir=$_work_item
  if ! is_ready_ $_work_item log_cif2qe.dat; then
    exit -1
  fi
  cd $_workdir
  cd qe
  srun --exclusive -N 1 -n 24 -c 4 pw.x -nk 24 -in scf.in > scf.out
}
export -f task_scf

date
echo "  scf"
cat $@ | parallel -j `find_multiplicity_ 1` --jl log_scf.dat --resume task_scf {} {%}

function task_copy_work () {
  set -e
  _work_item=$1
  _slot_id=$2
  _workdir=$_work_item
  if ! is_ready_ $_work_item log_scf.dat; then
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
cat $@ | parallel -j `find_multiplicity_ 1` --jl log_copy_work.dat --resume task_copy_work {} {%}

function task_nscf () {
  set -e
  _work_item=$1
  _slot_id=$2
  _workdir=$_work_item
  if ! is_ready_ $_work_item log_copy_work.dat; then
    exit -1
  fi
  cd $_workdir
  cd qe/check_wannier
  sed -e "s/electrons/electrons\n  diagonalization = 'cg'/g" nscf.in > nscf_cg.in
  srun --exclusive -N 1 -n 64 -c 2 pw.x -nk 64 -in nscf_cg.in > nscf.out
}
export -f task_nscf

date
echo "  nscf"
cat $@ | parallel -j `find_multiplicity_ 1` --jl log_nscf.dat --resume task_nscf {} {%}

function task_band () {
  set -e
  _work_item=$1
  _slot_id=$2
  _workdir=$_work_item
  if ! is_ready_ $_work_item log_nscf.dat; then
    exit -1
  fi
  cd $_workdir
  cd qe/band
  sed -e "s/electrons/electrons\n  diagonalization = 'cg'/g" nscf.in > nscf_cg.in
  srun --exclusive -N 1 -n 64 -c 2 pw.x -nk 64 -in nscf_cg.in > nscf.out
  srun --exclusive -N 1 -n 64 -c 2 bands.x -nk 64 -in band.in > band.out
}
export -f task_band

date
echo "  band"
cat $@ | parallel -j `find_multiplicity_ 1` --jl log_band.dat --resume task_band {} {%}

function task_nscf2 () {
  set -e
  _work_item=$1
  _slot_id=$2
  _workdir=$_work_item
  if ! is_ready_ $_work_item log_band.dat; then
    exit -1
  fi
  cd $_workdir
  cd qe
  sed -e "s/electrons/electrons\n  diagonalization = 'cg'/g" nscf.in > nscf_cg.in
  srun --exclusive -N 1 -n 64 -c 2 pw.x -nk 64 -in nscf_cg.in > nscf_cg.out
}
export -f task_nscf2

date
echo "  nscf2"
cat $@ | parallel -j `find_multiplicity_ 1` --jl log_nscf2.dat --resume task_nscf2 {} {%}

echo "done."

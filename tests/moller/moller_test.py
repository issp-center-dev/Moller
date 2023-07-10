import os, sys
import time
import random
from mpi4py import MPI

def task(task_name, delay, fail):
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    proc = MPI.Get_processor_name()

    nthr = os.getenv("OMP_NUM_THREADS")

    proclist = comm.gather(proc, root=0)
    if rank == 0:
        proctable = {}
        for p in proclist:
            proctable[p] = proctable.get(p, 0) + 1
    
    is_failed = random.randint(1,100) <= int(fail)
    delay_time = random.normalvariate(mu=delay, sigma=delay*0.2)

    if rank == 0:
        print(f"{task_name}: nproc={size}, nthread={nthr}, host={proctable}, delay={delay_time:.3f}, fail={is_failed}")

    time.sleep(delay_time)

    if rank == 0 and is_failed:
        sys.exit(1)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(prog='moller_test')
    parser.add_argument('task_name', nargs='?', default=None, help='task name')
    parser.add_argument('-s', '--sleep', nargs='?', default=0, help='sleep duration (sec)')
    parser.add_argument('-f', '--fail', nargs='?', default=0, help='failure rate (%)')

    args = parser.parse_args()

    task(args.task_name, int(args.sleep), int(args.fail))

if __name__ == '__main__':
    main()

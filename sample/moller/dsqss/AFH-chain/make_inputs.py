import subprocess
import os

from dsqss.dla_pre import dla_pre
from dsqss.result import Results


lattice = {"lattice": "hypercubic", "dim": 1, "L": 8}
hamiltonian = {"model": "spin", "Jz": -1, "Jxy": -1}
parameter = {"nset": 10, "ntherm": 1000, "ndecor": 1000, "nmcs": 10000,
             "wvfile": "wv.xml", "dispfile": "disp.xml"}

Ls = [8, 16, 32, 64, 128]
Ms = [1, 2]
Ts = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.25, 1.5, 1.75, 2.0]

os.makedirs("output", exist_ok=True)
os.chdir("output")
f_list = open("list.dat", "w")
for M in Ms:
    for L in Ls:
        for i, T in enumerate(Ts):
            lattice["L"] = L
            hamiltonian["M"] = M
            parameter["beta"] = 1.0 / T
            taskdir = f"L_{L}__M_{M}__T_{T}"
            f_list.write(f"{taskdir}\n")
            os.makedirs(taskdir, exist_ok=True)
            os.chdir(taskdir)
            dla_pre(
                {"parameter": parameter, "hamiltonian": hamiltonian, "lattice": lattice},
                "param.in",
            )
            with open("p.dat", "w") as f:
                f.write(f"{M} {L} {T}\n")
            os.chdir("..")

import sys
import os

if len(sys.argv) < 2:
    print("Usage: python extract_result.py <list.dat>")
    sys.exit(1)

fout = open("result.dat", "w")
fout.write("# M L T Xmean Xerr\n")

dirlist = open(sys.argv[1])
for dir in dirlist:
    dir = dir.strip()
    if dir == "":
        continue
    print(dir)
    with open(os.path.join(dir, "p.dat")) as f:
        words = f.readline().strip().split()
        M = int(words[0])
        L = int(words[1])
        T = float(words[2])
    with open(os.path.join(dir, "sample.log")) as f:
        Xmean = float("nan")
        Xerr = float("nan")
        for line in f:
            words = line.strip().split()
            if len(words)>0 and words[1] == "xmzu":
                Xmean = float(words[3])
                Xerr = float(words[4])
        fout.write(f"{M} {L} {T} {Xmean} {Xerr}\n")
fout.close()

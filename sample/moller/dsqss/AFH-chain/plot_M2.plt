set auto
set size 1.0
set style data yerrorline
set key bottom

set xl "T"
set yl "{/Symbol c}"

set xtics 0.25
set ytics 0.05

# phenomelogical curve in thermodynamic limit
# S=1 [J. Souletie et al, PRB 70, 054410 (2004)]
f_2(b) = (0.125 * exp(-0.451*b) + 0.564 * exp(-1.793*b)) *b

plot \
f_2(1.0/x) lc rgb "black" dt (10,10) t"phenomelogical curve", \
"< awk '$1 == 2 && $2 == 8 {print}' output/result.dat" u 3:4:5  t"L=8",\
"< awk '$1 == 2 && $2 == 16 {print}' output/result.dat" u 3:4:5 t"L=16",\
"< awk '$1 == 2 && $2 == 32 {print}' output/result.dat" u 3:4:5 t"L=32",\
"< awk '$1 == 2 && $2 == 64 {print}' output/result.dat" u 3:4:5 t"L=64",\
"< awk '$1 == 2 && $2 == 128 {print}' output/result.dat" u 3:4:5 t"L=128"


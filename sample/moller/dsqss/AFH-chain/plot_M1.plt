set auto
set size 1.0
set key bottom
set style data yerrorline

set xl "T"
set yl "{/Symbol c}"

set xtics 0.25
set ytics 0.05

# phenomelogical curve in thermodynamic limit
# S=1/2 [W. E. Estes et al, Inorganic Chemistry 17, 1415 (1978)]
f_1(b) = ((0.25 + 0.14995*0.5*b + 0.30094*0.25*b**2)/(1.0 + 1.9852*0.5*b+0.68854*0.25*b**2+6.0626*0.125*b**3)) * b

plot \
f_1(1.0/x) lc rgb "black" dt (10,10) t"phenomelogical curve",\
"< awk '$1 == 1 && $2 == 8 {print}' output/result.dat" u 3:4:5  t"L=8",\
"< awk '$1 == 1 && $2 == 16 {print}' output/result.dat" u 3:4:5 t"L=16",\
"< awk '$1 == 1 && $2 == 32 {print}' output/result.dat" u 3:4:5 t"L=32",\
"< awk '$1 == 1 && $2 == 64 {print}' output/result.dat" u 3:4:5 t"L=64",\
"< awk '$1 == 1 && $2 == 128 {print}' output/result.dat" u 3:4:5 t"L=128"

Lmax=18
# L in 8, 10, ..., Lmax
for L in $(seq 8 2 $Lmax); do
  dirname=L_${L}
  mkdir -p $dirname
  cp stan.in $dirname
  echo "L = ${L}" >> $dirname/stan.in
  echo $dirname >> list.dat
done

rm -f extract_gap.sh
cat > extract_gap.sh << EOF
rm -f gap.dat
for L in \$(seq 8 2 $Lmax); do
  echo -n "\${L} " >> gap.dat
  dirname=L_\${L}
  cat \$dirname/gap.dat >> gap.dat
done
EOF

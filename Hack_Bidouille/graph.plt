set xlabel 'Temps (années)'
set ylabel 'Coût (€)'

unset key

set style line 1 lc rgb '#0060ad' lt 1 lw 2 pt 7 ps 1.5   # --- bleu
set style line 2 lc rgb '#dd181f' lt 1 lw 2 pt 5 ps 1.5   # --- rouge
set style line 3 lc rgb '#c200f2' lt 1 lw 2 pt 3 ps 1.5   # --- violet

set label 1 'Raspberry Pi' at 1.5,120 front center textcolor ls 1
set label 2 'SMSSystem' at 2.5,900 textcolor ls 2
set label 3 'Pianotier' at 2.3,500 right textcolor ls 3

plot 'money.dat' i 0 u 1:2 with linespoints ls 1 title "Raspberry Pi", \
     ''          i 1 u 1:2 with linespoints ls 2 title "SMSSystem", \
     ''          i 2 u 1:2 with linespoints ls 3 title "Pianotier"


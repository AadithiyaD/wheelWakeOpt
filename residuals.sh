#!/bin/sh

logFile="log.simpleFoam"
imgName="residuals"

gnuplot <<- PLT
set terminal pngcairo font "helvetica,20" size 1000,1000
set format y "10^{%L}"
set logscale y
set title "Residuals"
set ylabel 'Residual'
set xlabel 'Iteration'
set output './$imgName.png'
set y2tics
set y2label 'Cumulative Continuity (linear)' tc "black"

plot "< cat $logFile | grep 'Solving for Ux' | cut -d' ' -f9 | tr -d ','" title 'Ux' with lines lc "red" lw 2,\
"< cat $logFile | grep 'Solving for Uy' | cut -d' ' -f9 | tr -d ','" title 'Uy' with lines lc "blue" lw 2,\
"< cat $logFile | grep 'Solving for Uz' | cut -d' ' -f9 | tr -d ','" title 'Uz' with lines lc "green" lw 2,\
"< cat $logFile | grep 'Solving for omega' | cut -d' ' -f9 | tr -d ','" title 'omega' with lines lc "magenta" lw 2,\
"< cat $logFile | grep 'Solving for epsilon' | cut -d' ' -f9 | tr -d ','" title 'epsilon' with lines lc "orange" lw 2,\
"< cat $logFile | grep 'Solving for Rwa' | cut -d' ' -f9 | tr -d ','" title 'Rwa' with lines lc "magenta" lw 2,\
"< cat $logFile | grep 'Solving for k' | cut -d' ' -f9 | tr -d ','" title 'k' with lines lc "forest-green" lw 2,\
"< cat $logFile | grep 'Solving for p' | cut -d' ' -f9 | tr -d ','" title 'p' with lines lc "navy" lw 2,\
"< cat $logFile | grep 'time step continuity errors' | cut -d ' ' -f15 | tr -d ','" title 'cumulative continuity' with lines lc "black" lw 2 axes x1y2
PLT

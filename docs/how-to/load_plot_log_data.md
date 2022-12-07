# How to parse, load and plot information contained in the Nek5000 log

Nek5000 log is difficult to understand but contains important data on the simulation:

```
Step      2, t= 1.4102940E-01, DT= 7.0514701E-02, C=  1.398 4.6482E-01 4.6482E-01
             Solving for fluid
          2  PRES gmres         5   3.1277E-06   3.7775E-04   1.0000E-05   5.5211E-02   8.2769E-02    F
          2  Hmholtz VELX       4   2.5189E-08   9.3788E-02   1.0000E-07
          2  Hmholtz VELY       4   2.5189E-08   9.3788E-02   1.0000E-07
          2  Hmholtz VELZ       4   3.5489E-08   1.3213E-01   1.0000E-07
             L1/L2 DIV(V)           9.0707E-20   5.2770E-06
             L1/L2 QTL              0.0000E+00   0.0000E+00
             L1/L2 DIV(V)-QTL       9.0707E-20   5.2770E-06
          2  Fluid done  1.4103E-01  2.3652E-01
```

The object `sim.output.print_stdout` (see
{class}`snek5000.output.print_stdout.PrintStdOut`) provides utilities to load and
represent this information. Some possibilities are presented in
[a section of the tutorial using `snek5000-tgv`](../tuto_tgv.myst.md#parse-load-and-plot-information-contained-in-the-nek5000-log).

# State of art

The CFD framework Nek5000 is the culmination of several decades of development.
Nek5000 solvers can produce high-fidelity simulations owing to spectral-element
method and can scale upto several thousands of cores [@nek5000_scaling].
Development of Nek5000 is primarly driven by performance optimization,
incorporating new numerical method whilst following a keep-it-simple approach
to ensure portability across various HPC machines.

Development of Nek5000 continues to this day with efforts underway to use GPUs
[@nek5000_openacc] and to rewrite it in C++ [@nekrs] and modern Fortran
[@neko].

## Statement of need

Snek5000 enhances the user-experience by addressing the following downsides of
using a typical Nek5000 solver:

1. Only a limited set of utilities come packaged with Nek5000 and those focus
   on compilation and mesh-generation. As a result, usability of Nek5000 takes
   a hit and a practitioner is left to construct a homebrewn solution to
   conduct exploratory research and parametric studies. Snek5000 functions as a
   workflow manager for assisting packaging, setup, compilation and
   post-processing aspects of a simulation.

2. The simulation parameters are spread in at least three different files (
   `*.box`, `*.par` and `SIZE`). Some parameters have short and cryptic names
   (for example, `lx1`, `lxd` etc.) and are dependent on each other. Snek5000 tries
   to provide good defaults and [dynamically set some of these
   parameters](https://snek5000.readthedocs.io/en/stable/_generated/snek5000.operators.html#snek5000.operators.Operators)
   when possible, allowing a user to get started the need to master the whole
   manual.

To the best of the authors' knowledge no other actively maintained and reusable
approaches have been made to wrap Nek5000. A project called `nekpy` [@nekpy]
was the only known prior work resembling Snek5000, where it uses templated
source files to fill in parameters.

In the future, Snek5000 can also function as a compatibility layer to migrate
to upcoming rewrites of Nek5000 which require some extra input files [@nekrs,
@neko].

Notes on Nek5000 internals
##########################

Boundary condition
==================

Algorithm
---------

The following describes the flow of logic in setting the boundary
conditions.

In ``drive1.f``:

-  :c:func:`nek_advance`: single timestep if Pn/Pn-2

   -  ``igeom=1``: RHS terms
   -  ``igeom=2``: Actual
   -  ``call heat``
   -  ``call fluid`` -> drive2.f

-  :c:func:`fluid`:

   -  ``iftran=1,ifrich=0`` -> :c:func:`plan3` in ``planx.f``

-  :c:func:`plan3`: Helmholtz operator split into two steps ``igeom=1,2``

   -  :c:func:`makef` : extrapolate pressure, solve for intermadiate velocity
   -  solve for update of pressure, velocity divergence free. Only
      approximate operator is used here, because the exact one requires
      Helmholtz operator.
   -  Block LU decomposition -> Consistent Helmholtz operator
   -  Boundary condition is not required for the second step.
      Preconditioner.
   -  See Blair Perot (1993)

Also if ``igeom=2``:

-  ``sethlm``: ``h1=diffusion`` ``h2=helmholtz operator``
-  :c:func:`cresvif` compute residual:

   -  lagvel, save velocity field
   -  ``bcdirvc``: boundary dirichlet velocity, ``bcneutr``: boundary
      neutral -> ``bdry.f``
   -  ``opgradt``: extrapolate pressire in time
   -  add residual

-  ``ophinv``, ``opadd2``: inverse helmholtz
-  :c:func:`incomprn`:

   -  Project velocity
   -  ``opgradt``: pressure
   -  ``opbinv`` -> ``navier1``:

      -  bdry?
      -  ``opmask``: set 0 to dirichlet BC, masked from the update

Boundary condition subroutines
------------------------------

Periodicity: node numbering

``bcdirvc``: Dirichlet
~~~~~~~~~~~~~~~~~~~~~~

-  ``CB = V (Constant Dirichlet in rea file)``
-  ``CB = v (user provided Dirichlet in userbc)``:

   -  ``FACEIV``: works on temporary arrays ``tmp1, tmpr3``

      -  facind: face index
      -  ``facev`` -> ``userbc``
      -  ``opdsop``: max min, to get consistent bc shared nodes
      -  if not stress forulation ``ifstrs``:

         -  ``add2`` -> Velocity + Tmp

``bcneutr``: Neumann transient?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

No mask

-  ``chkcbc``: alignment check

-  ``SYM`` <- called ``bcmask`` <->= ``nek_init`` modifies the masking
   for one component

-  Also by ``sethmsk``

-  ``b1mask``, ``b2mask``, ``b3mask`` arrays:

-  FEM trick, if you don’t anything: **Natural BC**. Normal stresses are
   0, BC is the fluxes on the last element.

``subs2.f``

-  ``sh``: ``faceiv`` -> sets traction array TRX, TRY, TRZ -> as
   acceleration

-  ``faccvs`` -> multiplies by the surface area -> force

-  ``globrot``, does rotation with respect to global coordinates

-  added to RHS: ``bfx``, ``bfy`` -> acceleration

Velocity should be ``v=0``

Caution: Pressure preconditioner and BC are related

.. todo::

   Set velocity v=0, normal component of velocity is zero, opposite of ``on``
   boundary condition.

Time-stepping algebra
=====================

Mass matrix requires time levels (n, n-1, n-2): extrapolated Conv /
Stiffness requires time levels (n-1, n-2): explicit

Comparison with Adams-Bashforth
-------------------------------

AB2: needs previous RHS BDF: needs previous LHS

Why not: Runge-Kutta?
---------------------

According to mathematicians, it is not clear because you have a pressure
correction in each sub-step.

CFL number
----------

BDF3/EXT3: CFL=0.6. Characteristic method

Filtering
=========

Filtering in Nek5000 is controlled by 

We prefer to use HPFRT (high-pass filtering with relaxation term) in Nek5000. 
There is also an 

HPFRT vs explicit filtering
---------------------------

Similarities
~~~~~~~~~~~~

- Both methods aims to extract energy from higher modes of the solution.
- Filtering weight determines the strength of the filter
- Filter cut-off ratio determines the what part of the spectrum is diffused
  numerically by the filter,

Differences
~~~~~~~~~~~

- HPFRT introduces a term in the RHS of the governing equations, thereby
  not violating zero velocity divergence, or in other words behaving like a source
  or sink.
- Explicit filtering is performed at the end of the time step, and very likely
  could result in velocity divergence. 

Filtering as a sponge-layer
---------------------------
Filter weight can be varied within the domain, and this would allow the filter to
behave like a sponge-layer if needed.
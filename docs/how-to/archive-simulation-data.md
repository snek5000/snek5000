# How to make a compressed archive of simulation data

Nek5000 simulations can generate a lot of data files. To reduce the strain in your HPC
facility, it is often recommended:

1. To limit the **number of files**
1. Reduce the **disk usage**

We can achieve both without erasing any data by using Snek5000 and efficient compression
tools namely [`zstandard`](https://en.wikipedia.org/wiki/Zstd) and preferably
[`bsdtar`](https://www.freebsd.org/cgi/man.cgi?query=bsdtar&sektion=1&format=html)
(usually faster) if not [GNU `tar`](https://www.gnu.org/software/tar/). If unavailable
some of these can be installed using conda / mamba:

```sh
conda install -c conda-forge zstandard tar
```

Once a simulation is done, you can create the archive using

```sh
cd path/to/sim
snek-make archive
```

The module which does the archiving is described [here](snek5000.util.archive).

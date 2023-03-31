---
title: 'Snek5000: Python framework for Nek5000'
tags:
  - CFD
  - Python
  - Nek5000
  - FluidSim
  - Snakemake
authors:
  - name: Ashwin Vishnu Mohanan
    orcid: 0000-0002-2979-6327
    equal-contrib: true
    affiliation: 1
  - name: Arman Khoubani
    orcid: 0000-0002-0295-5308
    equal-contrib: true
    affiliation: 2
  - name: Pierre Augier
    orcid: 0000-0001-9481-4459
    equal-contrib: true
    affiliation: 2
affiliations:
  - name: Swedish Meteorological and Hydrological Institute, Norrk{\"o}ping, Sweden
    index: 1
  - name: Laboratoire des \'Ecoulements G\'eophysiques et Industriels, Universit\'e~Grenoble~Alpes,
      CNRS, Grenoble~INP, 38000~Grenoble, France
    index: 2
date: 2 March 2023
bibliography: paper.bib
---

# Summary

Computational fluid dynamics (CFD) simulations are essential tools in various scientific and engineering disciplines. The Nek5000 CFD code, a spectral element solver, has a proven track record in numerous applications. Snek5000 is a Python package designed to streamline the management and visualization of fluid dynamics simulations based on the Nek5000 Fortran CFD code. The package builds upon the functionality of Nek5000 by providing a user-friendly interface for launching and restarting simulations, loading simulation data, and generating figures and movies. This paper introduces Snek5000, discusses its design principles, and highlights its impact on the scientific community.

## Snek5000: Features and Capabilities

### Fluidsim Solvers

Snek5000 enables users to create Fluidsim solvers for simulations based on the Nek5000 library. Several open-source solvers, such as snek5000-phill, snek5000-cbox, and snek5000-tgv, are available, and users can easily develop custom solvers tailored to their specific Nek5000 cases. This flexibility allows researchers to adapt Snek5000 to a wide range of fluid dynamics problems and simulation requirements.

### Streamlined Simulation Management

With a Snek5000-Fluidsim solver, users can efficiently launch and restart simulations using Python scripts and terminal commands. This streamlines the process of managing simulations, freeing up time and resources for data analysis and understanding the underlying physics. The package also handles various file operations, such as directory creation and file copying, further simplifying simulation management.

### Loading Simulations and Data Visualization

Snek5000 simplifies the process of loading simulations, reading associated parameters and data, and generating visualizations, such as figures and movies. By utilizing popular Python packages, such as Matplotlib and Xarray, Snek5000 facilitates the creation of high-quality visualizations that can be easily customized to meet individual needs. This powerful visualization capability aids researchers in understanding complex fluid dynamics phenomena and effectively presenting their findings.

### Post-processing and Data Analysis

Beyond visualization, Snek5000 also provides tools for post-processing and data analysis. Users can easily load simulation data into Python for further processing, statistical analysis, and comparison between different simulations. This streamlined approach to data analysis enables researchers to gain valuable insights into their simulations and focus on the underlying physical processes.

### Powered by Python Packages

Snek5000 leverages a variety of Python packages, including Snakemake, Fluidsim, Pymech, Matplotlib, Jinja, Pytest, and Xarray, to deliver a robust and user-friendly workflow management tool for Nek5000. These packages provide a powerful foundation for Snek5000, enabling its seamless integration with existing Python-based workflows and enhancing its overall usability.

### Tutorials and Documentation

Snek5000 provides comprehensive documentation (https://snek5000.readthedocs.io/) and tutorials to guide users through its features and capabilities. These resources help new users quickly become familiar with Snek5000 and enable experienced users to explore advanced features and customization options. By providing thorough documentation, Snek5000 promotes its widespread adoption and fosters a vibrant community of users and developers.

### Future Developments and Enhancements

The Snek5000 development team is committed to continuously improving the package and incorporating user feedback to address evolving needs within the scientific community.

# Statement of need

Snek5000 is a powerful and versatile Python package designed to streamline the management and visualization of Nek5000-based fluid dynamics simulations. By providing an efficient interface for creating solvers, launching and restarting simulations, and generating visualizations, Snek5000 enables researchers to focus on scientific discovery and understanding complex fluid dynamics problems. With its open-source nature, comprehensive documentation, and active development, Snek5000 has the potential to significantly impact the fluid dynamics research community and drive further advancements in the field.

# Acknowledgements

We acknowledge ...

# References

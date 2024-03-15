=======
GSAS-II
=======

[![Actions Status][actions-badge]][actions-link]
[![Documentation Status][rtd-badge]][rtd-link]

[![PyPI version][pypi-version]][pypi-link]
[![Conda-Forge][conda-badge]][conda-link]
[![PyPI platforms][pypi-platforms]][pypi-link]

[![GitHub Discussion][github-discussions-badge]][github-discussions-link]

<!-- SPHINX-START -->

<!-- prettier-ignore-start -->
[actions-badge]:            https://github.com/AdvancedPhotonSource/GSAS-II/workflows/CI/badge.svg
[actions-link]:             https://github.com/AdvancedPhotonSource/GSAS-II/actions
[conda-badge]:              https://img.shields.io/conda/vn/conda-forge/GSAS-II
[conda-link]:               https://github.com/conda-forge/GSAS-II-feedstock
[github-discussions-badge]: https://img.shields.io/static/v1?label=Discussions&message=Ask&color=blue&logo=github
[github-discussions-link]:  https://github.com/AdvancedPhotonSource/GSAS-II/discussions
[pypi-link]:                https://pypi.org/project/GSAS-II/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/GSAS-II
[pypi-version]:             https://img.shields.io/pypi/v/GSAS-II
[rtd-badge]:                https://readthedocs.org/projects/GSAS-II/badge/?version=latest
[rtd-link]:                 https://GSAS-II.readthedocs.io/en/latest/?badge=latest

<!-- prettier-ignore-end -->


GSAS-II is a unique and comprehensive Python project for
the calibration, reduction and analysis of all types of x-ray and neutron
diffraction data, including single-crystal and powder data, including
constant-wavelength, pink-beam and time-of-flight data types and from lab,
synchrotron, spallation and reactor sources. Its primary use is for 
determination of crystal structures and diffraction-based materials
characterization for crystalline solids on all scales, from
perovskites through protein. Refinements can
combine measurements from multiple data types and large groups of data
can be analyzed together  via "sequential fitting". It also
provides powerful and flexible capabilities for integration of 2D
powder diffraction image data.
In addition to single-crystal and powder diffraction, GSAS-II
offers small-angle scattering and reflectometry analysis, structure
solution capabilities and interfaces to several other types of
analysis tools, such as for pair distribution functions, faulted
materials, maximum entropy Fourier maps and symmetry analysis.

GSAS-II offers extensive visualization
capabilities and a complete GUI implementation. An
applications-interface (API) allows for scripted use of much of the
GSAS-II functionality. 

Many capabilities of GSAS-II are unique to GSAS-II or are only found
in software with very limited scope. For magnetic scattering, all
possible color subgroups can be derived and explored. For
incomensurate structures, a generalized form of 3+1 superstructures
can be handled. From powder
diffraction, GSAS-II supports all stages of data reduction and
analysis, including area detector calibration and integration, pattern
indexing, LeBail and Pawley intensity extraction and peak
fitting. Pair distribution functions (PDF) can be computed from
high-energy x-ray diffraction. Instrumental profile parameters can be
fit to data from standards or derived from fundamental parameters;
sample profile effects (crystallite size and microstrain) are treated
independently from the instrument. Sequential fitting is a novel
process that allows
large numbers of data sets, 
measured with parametric changes in measurement settings, to be fit
single refinement with subsequent parametric fitting. 

GSAS-II is freely distributed as open source software and runs on Windows,
MacOS, Linux and Raspberry Pi computers. It currently receives >600
citations/year. 

* Please Cite: the primary citation for GSAS-II is:

    Toby, B. H., & Von Dreele, R. B. (2013). "GSAS-II: the genesis of
    a modern open-source all purpose crystallography software
    package". Journal of Applied Crystallography, 46(2),
    544-549. ​doi:10.1107/S0021889813003531 

    If you use GSAS-II in any part of your project, please cite it in your
    publications. This is the most valuabe way you can demonstrate your support of
    the project.  Note that some sections of program utilize work by
    others and will display citations for that. If you use those sections,
    please cite those papers as well.  

* At present the home page for the software is here:
  https://subversion.xray.aps.anl.gov/trac/pyGSAS. Note installation
  instructions and tutorials at that URL.

* The main svn repository for the source code is:
  https://subversion.xray.aps.anl.gov/pyGSAS, but can be browsed here:
  https://subversion.xray.aps.anl.gov/trac/pyGSAS/browser 
* GSAS-II is in the process of a migration to GitHub. At present
  several "sandbox" development repositories are found in
  https://github.com/GSASII but these are all temporary.
* The permanent home for GSAS-II after migration is complete will be
  https://github.com/AdvancedPhotonSource/GSAS-II. At present a manually
  maintained "mirror" of the master svn repo is found here: 
  https://github.com/AdvancedPhotonSource/GSASII-copy. This copy may
  not always have the latest changes checked into svn, but will always
  match a recent release. Branches may be used to try out different
  PRs prior to the code update into svn. 

* GSAS-II is free and open source software, see the license file for
  more details. 
* Documentation: https://subversion.xray.aps.anl.gov/pyGSAS
* Code documentation: https://gsasii.readthedocs.io.


..   commented out for now
     Features
     --------

     * TODO


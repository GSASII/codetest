======================
*GSAS-II Misc Scripts*
======================

*testDeriv: Check derivative computation*
=========================================

Use this to check derivatives used in structure least squares
refinement against numerical values computed in this script.

.. automodule:: testDeriv
    :members: 

*GSASIItestplot: Plotting for testDeriv*
========================================

Plotting module used for script testDeriv.

.. automodule:: GSASIItestplot
    :members: 

*scanCCD: reduce data from scanning CCD*
========================================

Quickly prototyped routine for reduction of data from detector described in
B.H. Toby, T.J. Madden, M.R. Suchomel, J.D. Baldwin, and R.B. Von Dreele,
"A Scanning CCD Detector for Powder Diffraction Measurements".
Journal of Applied Crystallography. 46(4): p. 1058-63 (2013). This is
no longer being updated. 

.. automodule:: scanCCD
    :members: 

*makeMacApp: Create Mac Applet*
===============================

This script creates an AppleScript app bundle to launch GSAS-II. It is
called by bootstrap.py during the GSAS-II installation process. It
creates a "copy" of Python that is able to run wx.Python programs and
names this version of Python as GSAS-II so that items in the menus are
named correctly. 

.. automodule:: makeMacApp
    :members: 

*makeBat: Create GSAS-II Batch File*
====================================

This script performs Windows specific installation steps to allow for
easy launching of GSAS-II. It is
called by bootstrap.py during the GSAS-II installation process.

.. automodule:: makeBat
    :members: 

*makeLinux: Create Linux Shortcuts*
===================================

This script performs Linux specific installation steps that
allowscreates files allowing 
GSAS-II to be launched from a desktop icon or desktop manager menu.
Not all desktop managers will recognize these files. 
It is called by bootstrap.py during the GSAS-II installation process.

.. automodule:: makeLinux
    :members: 

*makeVarTbl: Make Table of Variable Names*
============================================

This creates a table of variable names from the definitions supplied
in :func:`GSASIIobj.CompileVarDesc`. This table is used in the
Sphinx documentation as the :ref:`GSAS-II Variable Names table <VarNames_table>`.
This is run as part of the Sphinx build from inside ``docs/source/conf.py``.

.. automodule:: makeVarTbl
    :members: 
       
*unit_tests: Self-test Module*
===================================

A script that can be run to test a series of self-tests in GSAS-II. 

.. automodule:: unit_tests
    :members: 

*testSytSym: Test Site Symmetry*
========================================

A GUI program for testing the site symmetry generation routines. 
       
.. automodule:: testSytSym
    :members: 

*testSSymbols: Test Superspace Group Symbols*
===============================================

A GUI program for testing the 3+1 superspace group symmetry generation routines. 
       
.. automodule:: testSSymbols
    :members: 


*Other scripts*
========================================

A few scripts are also placed in the GSAS-II auxiliary repositories 

``GSASII-buildtools/install/gitstrap.py``

    Used to install the GSAS-II package, including the appropriate
    binary files. May be used directly to install GSAS-II from inside
    Python in an appropriately configured Python installation, or
    is also used to obtain or update the GSAS-II files in a conda
    installation. 

``GSASII-buildtools/install/setgitversion.py``

   Used during the gsas2full (& gsas2complete) build process
   to modify the g2complete & g2full .template files to reflect the
   versions of Python & packages that should be used for builds. 

``GSASII-tutorials/scripts/makeGitTutorial.py``

   Provides a script to creates the HTML page
   (``GSASII/help/Tutorials.html``) that lists all the tutorials defined in
   variable :data:`GSASIIctrlGUI.tutorialIndex`. Run this after adding
   new tutorials to that catalog.

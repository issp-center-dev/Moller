****************************************************************
Introduction
****************************************************************

What is moller?
----------------------------------------------------------------

In recent years, the use of machine learning for predicting material properties and designing substances (known as materials informatics) has gained considerable attention.
The accuracy of machine learning depends heavily on the preparation of appropriate training data.
Therefore, the development of tools and environments for the rapid generation of training data is expected to contribute significantly to the advancement of research in materials informatics.

moller is provided as part of the HTP-Tools package, designed to support high-throughput computations.
It is a tool for generating batch job scripts for supercomputers and clusters, allowing parallel execution of programs under a series of computational conditions, such as parameter parallelism.
Currently, it supports the supercomputers ohtaka (using the slurm job scheduler) and kugui (using the PBS job scheduler) provided by the Institute for Solid State Physics, University of Tokyo.

License
----------------------------------------------------------------

The distribution of the program package and the source codes for moller follow GNU General Public License version 3 (GPL v3) or later.

Contributors
----------------------------------------------------------------

This software was developed by the following contributors.

-  ver.1.0-beta (Released on 2023/12/28)

   -  Developers

      -  Kazuyoshi Yoshimi (The Instutite for Solid State Physics, The University of Tokyo)

      -  Tatsumi Aoyama (The Instutite for Solid State Physics, The University of Tokyo)

      -  Yuichi Motoyama (The Instutite for Solid State Physics, The University of Tokyo)

      -  Masahiro Fukuda (The Instutite for Solid State Physics, The University of Tokyo)

      -  Kota Ido (The Instutite for Solid State Physics, The University of Tokyo)

      -  Tetsuya Fukushima (The National Institute of Advanced Industrial Science and Technology (AIST))

      -  Shusuke Kasamatsu (Yamagata University)

      -  Takashi Koretsune (Tohoku University)

   -  Project Corrdinator

      -  Taisuke Ozaki (The Instutite for Solid State Physics, The University of Tokyo)


Copyright
----------------------------------------------------------------

.. only:: html

  |copy| *2023- The University of Tokyo. All rights reserved.*

  .. |copy| unicode:: 0xA9 .. copyright sign

.. only:: latex

  :math:`\copyright` *2023- The University of Tokyo. All rights reserved.*

This software was developed with the support of "Project for advancement of software usability in materials science" of The Institute for Solid State Physics, The University of Tokyo.

Operating environment
----------------------------------------------------------------

moller was tested on the following platforms:

- Ubuntu Linux + python3


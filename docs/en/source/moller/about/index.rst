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
Currently, it supports the supercomputers ohtaka (using the slurm job scheduler) and kugui (using the PBS job scheduler) provided by the Institute for Solid State Physics, University of Tokyo, as well as generic PBS-based clusters and workstations without a job scheduler.

License
----------------------------------------------------------------

The distribution of the program package and the source codes for moller follow GNU General Public License version 3 or later (GPL-3.0-or-later).

Contributors
----------------------------------------------------------------

This software was developed by the following contributors.

-  ver.1.0.1 (Released on 2024/09/10)

-  ver.1.0.0 (Released on 2024/03/06)

-  ver.1.0-beta (Released on 2023/12/28)

   -  Developers

      -  Kazuyoshi Yoshimi (The Institute for Solid State Physics, The University of Tokyo)

      -  Tatsumi Aoyama (The Institute for Solid State Physics, The University of Tokyo)

      -  Yuichi Motoyama (The Institute for Solid State Physics, The University of Tokyo)

      -  Masahiro Fukuda (The Institute for Solid State Physics, The University of Tokyo)

      -  Kota Ido (The Institute for Solid State Physics, The University of Tokyo)

      -  Tetsuya Fukushima (The National Institute of Advanced Industrial Science and Technology (AIST))

      -  Shusuke Kasamatsu (Yamagata University)

      -  Takashi Koretsune (Tohoku University)

   -  Project Coordinator

      -  Taisuke Ozaki (The Institute for Solid State Physics, The University of Tokyo)


Copyright
----------------------------------------------------------------

.. only:: html

  |copy| *2023- The University of Tokyo. All rights reserved.*

  .. |copy| unicode:: 0xA9 .. copyright sign

.. only:: latex

  :math:`\copyright` *2023- The University of Tokyo. All rights reserved.*

This software was developed with the support of "Project for advancement of software usability in materials science" of The Institute for Solid State Physics, The University of Tokyo.

The installation of moller on Miyabi and Genkai was supported by JST Moonshot R&D Program (Grant Number JPMJMS24A3).

Citation
----------------------------------------------------------------

When publishing results obtained using this software, we would appreciate it if you cite the following paper:

  Kazuyoshi Yoshimi, Yuichi Motoyama, Tatsumi Aoyama, Mitsuaki Kawamura, and Naoki Kawashima,
  "Project for advancement of software usability in materials science",
  Science and Technology of Advanced Materials: Methods **5**, 2564055 (2025).
  `https://doi.org/10.1080/27660400.2025.2564055 <https://doi.org/10.1080/27660400.2025.2564055>`_

BibTeX entry:

.. code-block:: bibtex

  @article{Yoshimi2025,
    author  = {Kazuyoshi Yoshimi and Yuichi Motoyama and Tatsumi Aoyama and Mitsuaki Kawamura and Naoki Kawashima},
    title   = {Project for advancement of software usability in materials science},
    journal = {Science and Technology of Advanced Materials: Methods},
    volume  = {5},
    number  = {1},
    pages   = {2564055},
    year    = {2025},
    doi     = {10.1080/27660400.2025.2564055},
    url     = {https://doi.org/10.1080/27660400.2025.2564055}
  }

Operating environment
----------------------------------------------------------------

moller was tested on the following platforms:

- Ubuntu Linux + python3

moller is pre-installed and available on the following supercomputer systems:

- `ISSP supercomputers <https://mdcl.issp.u-tokyo.ac.jp/scc/en/>`_ (The University of Tokyo): kugui, ohtaka
- Tohoku University supercomputer: `AOBA <https://www.cc.tohoku.ac.jp/english/>`_
- Kyushu University supercomputer: `Genkai <https://www.cc.kyushu-u.ac.jp/scp/en/system/genkai/>`_

The following system is already supported by moller, while pre-installation is in progress (as of August 14, 2026):

- Information Technology Center, The University of Tokyo: `Miyabi <https://www.cc.u-tokyo.ac.jp/en/supercomputer/miyabi/service/>`_

For instructions on using moller on these systems, please refer to the user guide of each system.


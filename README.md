<div align="center">
<img src="docs/images/moller_logo.png" alt="moller logo" width="200">
</div>

# moller

[![Release](https://img.shields.io/github/v/release/issp-center-dev/Moller)](https://github.com/issp-center-dev/Moller/releases)
[![License: GPL-3.0-or-later](https://img.shields.io/badge/License-GPL--3.0--or--later-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.en.html)
[![Docs](https://github.com/issp-center-dev/Moller/actions/workflows/deploy_docs.yml/badge.svg)](https://github.com/issp-center-dev/Moller/actions/workflows/deploy_docs.yml)
[![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://www.python.org/)
[![DOI](https://img.shields.io/badge/DOI-10.1080%2F27660400.2025.2564055-blue)](https://doi.org/10.1080/27660400.2025.2564055)

In recent years, the use of machine learning for predicting material properties and designing substances (known as materials informatics) has gained considerable attention.
The accuracy of machine learning depends heavily on the preparation of appropriate training data.
Therefore, the development of tools and environments for the rapid generation of training data is expected to contribute significantly to the advancement of research in materials informatics.

moller is provided as part of the HTP-Tools package, designed to support high-throughput computations.
It is a tool for generating batch job scripts for supercomputers and clusters, allowing parallel execution of programs under a series of computational conditions, such as parameter parallelism.

## Supported platforms

- ISSP supercomputer systems: ohtaka, kugui
- general cluster machines and workstations

moller is pre-installed and available on the following supercomputer systems:

- [ISSP supercomputers](https://mdcl.issp.u-tokyo.ac.jp/scc/en/) (The University of Tokyo): kugui, ohtaka
- Tohoku University supercomputer: [AOBA](https://www.cc.tohoku.ac.jp/english/)
- Kyushu University supercomputer: [Genkai](https://www.cc.kyushu-u.ac.jp/scp/en/system/genkai/)

The following system is already supported by moller, while pre-installation is in progress (as of August 14, 2026):

- Information Technology Center, The University of Tokyo: [Miyabi](https://www.cc.u-tokyo.ac.jp/en/supercomputer/miyabi/service/)

For instructions on using moller on these systems, please refer to the user guide of each system.

## Requirement

Python3 with ruamel.yaml and other library packages and GNU Parallel.

## Install

- From source

``` bash
python3 -m pip install DIRECTORY_OF_THE_REPOSITORY
```

## License

The distribution of the program package and the source codes for moller follow
GNU General Public License version 3 or later
([GPL-3.0-or-later](https://www.gnu.org/licenses/gpl-3.0.en.html)).

Copyright (c) <2023-> The University of Tokyo. All rights reserved.

This software was developed with the support of
"Project for Advancement of Software Usability in Materials Science"
of The Institute for Solid State Physics, The University of Tokyo.

The installation of moller on Miyabi and Genkai was supported by
JST Moonshot R&D Program (Grant Number JPMJMS24A3).

## Citation

When publishing results obtained using this software, we would appreciate it if you cite the following paper:

> Kazuyoshi Yoshimi, Yuichi Motoyama, Tatsumi Aoyama, Mitsuaki Kawamura, and Naoki Kawashima,
> "Project for advancement of software usability in materials science",
> Science and Technology of Advanced Materials: Methods **5**, 2564055 (2025).
> [https://doi.org/10.1080/27660400.2025.2564055](https://doi.org/10.1080/27660400.2025.2564055)

BibTeX entry:

``` bibtex
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
```

## Official page

- [HTP-tools project page](https://www.pasums.issp.u-tokyo.ac.jp/htp-tools/)
- [Software repository](https://github.com/issp-center-dev/Moller)

## Authors

Kazuyoshi Yoshimi (ISSP, Univ. of Tokyo), 
Tatsumi Aoyama (ISSP, Univ. of Tokyo), 
Yuichi Motoyama (ISSP, Univ. of Tokyo), 
Masahiro Fukuda (ISSP, Univ. of Tokyo), 
Kota Ido (ISSP, Univ. of Tokyo), 
Tetsuya Fukushima (AIST), 
Shusuke Kasamatsu (Yamagata University), 
Takashi Koretsune (Tohoku University), 
Taisuke Ozaki (ISSP, Univ. of Tokyo)

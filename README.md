# moller

In recent years, the use of machine learning for predicting material properties and designing substances (known as materials informatics) has gained considerable attention.
The accuracy of machine learning depends heavily on the preparation of appropriate training data.
Therefore, the development of tools and environments for the rapid generation of training data is expected to contribute significantly to the advancement of research in materials informatics.

moller is provided as part of the HTP-Tools package, designed to support high-throughput computations.
It is a tool for generating batch job scripts for supercomputers and clusters, allowing parallel execution of programs under a series of computational conditions, such as parameter parallelism.

## Supported platforms

- ISSP supercomputer systems: ohtaka, kugui
- general cluster machines and workstations

## Requirement

Python3 with ruamel.yaml and other library packages and GNU Parallel.

## Install

- From source

``` bash
python3 -m pip install DIRECTORY_OF_THE_REPOSITORY
```

## License

The distribution of the program package and the source codes for moller follow
GNU General Public License version 3
([GPL v3](https://www.gnu.org/licenses/gpl-3.0.en.html)).

Copyright (c) <2023-> The University of Tokyo. All rights reserved.

This software was developed with the support of
"Project for Advancement of Software Usability in Materials Science"
of The Institute for Solid State Physics, The University of Tokyo.

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

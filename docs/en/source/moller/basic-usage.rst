Installation and basic usage
================================================================

**Prerequisite**

  Comprehensive calculation utility ``moller`` included in HTP-tools requires the following programs and libraries:

  - Python 3.x
  - ruamel.yaml module
  - tabulate module
  - GNU Parallel

.. **Official pages**
.. 
..   - `GitHub repository <https://github.com/issp-center-dev/HTP-tools-dev>`_

.. **Downloads**
.. 
..   HTP-tools can be downloaded by the following command with git:
.. 
..   .. code-block:: bash
.. 
..    $ git clone git@github.com:issp-center-dev/HTP-tools-dev.git

**Downloads**

  *The source package is not yet publicly available.*
   
**Installation**

  Once the source files are obtained, you can install HTP-tools by running the following command. The required libraries will also be installed automatically at the same time.

  .. code-block:: bash

     $ cd ./HTP-tools-dev
     $ python3 -m pip install .

  The executable files ``moller`` and ``moller_status`` will be installed.

**Directory structure**

  ::

     .
     |-- LICENSE
     |-- README.md
     |-- pyproject.toml
     |-- docs/
     |   |-- ja/
     |   |-- en/
     |   |-- tutorial/
     |-- src/
     |   |-- moller/
     |       |-- __init__.py
     |       |-- main.py
     |       |-- platform/
     |       |   |-- __init__.py
     |	     |   |-- base.py
     |	     |   |-- base_slurm.py
     |	     |   |-- base_pbs.py
     |	     |   |-- base_default.py
     |	     |   |-- ohtaka.py
     |	     |   |-- kugui.py
     |	     |   |-- default.py
     |	     |   |-- function.py
     |	     |   |-- utils.py
     |	     |-- moller_status.py
     |-- sample/

**Basic usage**

  ``moller`` is a tool to generate batch job scripts for supercomputers in which programs are run in parallel for a set of execution conditions using concurrent execution features.

  #. Prepare job description file

      First, you need to create a job description file in YAML format that describes the tasks to be executed on supercomputers. The details of the format will be given in File Format section of the manual.

  #. Run command

      Run moller program with the job description file, and a batch job script will be generated.

      .. code-block:: bash

          $ moller -o job.sh input.yaml

  #. Run batch jobs

      Transfer the generated batch job scripts to the supercomputer. Prepare a directory for each parameter set, and create a list of the directory names in a file ``list.dat``.

      Once the list file is ready, you may submit a batch job. The actual command may depend on the system. For example, for the system using slurm job scheduler (c.f. ISSP system B (ohtaka)), you may type in as follows:

      .. code-block:: bash

          $ sbatch job.sh list.dat

      After the job finishes, you may run the following command

      .. code-block:: bash

          $ moller_status input.yaml list.dat

      to obtain a report whether the calculation for each parameter set has been completed successfully.

**References**

[1] `O. Tange, GNU Parallel - The command-Line Power Tool, ;login: The USENIX Magazine, February 2011:42-47. <https://www.usenix.org/publications/login/february-2011-volume-36-number-1/gnu-parallel-command-line-power-tool>`_

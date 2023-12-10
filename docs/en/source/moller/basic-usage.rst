Installation and basic usage
================================================================

**Prerequisite**

  Comprehensive calculation utility ``moller`` included in HTP-tools requires the following programs and libraries:

  - Python 3.x
  - ruamel.yaml module
  - tabulate module
  - GNU Parallel

**Official pages**

  - `GitHub repository <https://github.com/issp-center-dev/Moller>`_

**Downloads**

  moller can be downloaded by the following command with git:

  .. code-block:: bash

    $ git clone https://github.com/issp-center-dev/Moller.git

**Installation**

  Once the source files are obtained, you can install moller by running the following command. The required libraries will also be installed automatically at the same time.

  .. code-block:: bash

     $ cd ./Moller
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

      Transfer the generated batch job scripts to the supercomputer.
      Prepare a directory for each parameter set, and create a list of the directory names in a file ``list.dat``.
      Note that the directory must be placed directly under the directory where the batch job is executed.

      Once the list file is ready, you may submit a batch job. The actual command depends on the system.

      - In case of ISSP system B (ohtaka)

        In ohtaka, slurm is used for the job scheduling system. In order to submit a batch job, a command ``sbatch`` is invoked with the job script as an argument. Parameters can be passed to the script as additional arguments; the name of list file is specified as a parameter.

        .. code-block:: bash

            $ sbatch job.sh list.dat

        If the list file is not specified, ``list.dat`` is used by default.

      - In case of ISSP system C (kugui)

        In kugui, PBS is used for the job scheduling system. In order to submit a batch job, a command ``qsub`` is invoked with the job script. There is no way to pass parameters to the script, and thus the name of the list file is fixed to ``list.dat``.

        .. code-block:: bash

            $ qsub job.sh

  #. Check the status of the calculation

      After the job finishes, you may run the following command

      .. code-block:: bash

          $ moller_status input.yaml list.dat

      to obtain a report whether the calculation for each parameter set has been completed successfully.


  #. Retry/resume job

        In case the job is terminated during the execution, the job may be resumed by submitting the batch job again with the same list file.
        The yet unexecuted jobs (as well as the unfinished jobs) will be run.


        - In case of ISSP system B (ohtaka)

        .. code-block:: bash

          $ sbatch job.sh list.dat

        To retry the failed tasks, the batch job is submitted with ``--retry`` command line option.

        .. code-block:: bash

          $ sbatch job.sh --retry list.dat

        - In case of ISSP system C (kugui)

        For kugui, to retry the failed tasks, the batch job script should be edited so that ``retry=0`` is changed to be ``retry=1``.

        .. code-block:: bash

          $ qsub job.sh

        Then, the batch job is submitted as above.

**References**

[1] `O. Tange, GNU Parallel - The command-Line Power Tool, ;login: The USENIX Magazine, February 2011:42-47. <https://www.usenix.org/publications/login/february-2011-volume-36-number-1/gnu-parallel-command-line-power-tool>`_

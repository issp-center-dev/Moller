.. _sec-tutorial:

Tutorial
================================================================

The procedure to use the batch job script generator ``moller`` consists of the following steps:
First, a job description file is prepared that defines the tasks to be executed. Next, the program ``moller`` is to be run with the job description file, and a batch job script is generated. The script is then transferred to the target supercomputer system. A batch job is submitted with the script to perform calculations.
In this tutorial, we will explain the steps along a sample in ``docs/tutorial/moller``.

Prepare job description file
----------------------------------------------------------------

A job description file describes the content of calculations that are carried out in a batch job.
Here, a *batch job* is used for a set of instructions submitted to job schedulers running on supercomputer systems. On the other hand, for the concurrent execution of programs that ``moller`` handles, we call a series of program executions performed for one set of parameters by a *job*. A job may consist of several contents that we call *tasks*. ``moller`` organizes job execution so that each task is run in parallel, and the synchronization between the jobs is taken at every start and end of the tasks.

.. only:: html

  .. figure:: ../../_static/task_view.png
     :alt: Tasks and jobs

     An example of tasks and jobs: Three jobs #1 ... #3 are carried out within a single batch job. Each job corresponds to different set of parameters. A job consists of 4 tasks. Each task is run in parallel among these three jobs.

.. only:: latex

  .. figure:: ../../_static/task_view.pdf
     :scale: 100%
     :alt: Tasks and jobs

     An example of tasks and jobs: Three jobs #1 ... #3 are carried out within a single batch job. Each job corresponds to different set of parameters. A job consists of 4 tasks. Each task is run in parallel among these three jobs.

An example of job description file is presented in the following. A job description file is in text-based YAML format. It contains parameters concerning the platform and the batch job, task descriptions, and pre/post-processes. See :ref:`File format <sec-fileformat>` section for the details.

.. literalinclude:: ../../../../tutorial/moller/input.yaml


Generate batch job script
----------------------------------------------------------------

``moller`` is to be run with the job description file (``input.yaml``) as an input as follows:

.. code-block:: bash

  $ moller -o job.sh input.yaml

A batch job script is generated and written to a file specified by the parameter in the job description file, or the command line option ``-o`` or ``--output``. If both specified, the command line option is used. If neither specified, the result is written to the standard output.

The obtained batch job script is to be transferred to the target system as required. It is noted that the batch job script is prepared for ``bash``; users may need to set the shell for job execution to ``bash``. (A care should be needed if the login shell is set to csh-type.)


Create list file
----------------------------------------------------------------

A list of jobs is to be created. ``moller`` is designed so that each job is executed within a directory prepared for the job with the job name. They are assumed to be placed in the directory in which the batch job runs. The job list can be created, for example, by the following command:

.. code-block:: bash

  $ /usr/bin/ls -1d > list.dat

In this tutorial, an utility script ``make_inputs.sh`` is enclosed which generates datasets and a list file.
  
.. code-block:: bash

  $ bash ./make_inputs.sh

By running the above command, a directory ``output`` and a set of subdirectories ``dataset-0001`` ... ``dataset-0020`` that correspond to datasets, and a list file ``list.dat`` are created.


Run batch job
----------------------------------------------------------------

The batch job is to be submitted to the job scheduler with the batch job script. In the following examples, we present two cases using ISSP system B (ohtaka) and C (kugui).

- In case of ISSP system B (ohtaka)

  In ohtaka, slurm is used for the job scheduling system. In order to submit a batch job, a command ``sbatch`` is invoked with the job script as an argument. Parameters can be passed to the script as additional arguments; the name of list file is specified as a parameter.
  
  .. code-block:: bash

      $ sbatch job.sh list.dat

  If the list file is not specified, ``list.dat`` is used by default.

- In case of ISSP system C (kugui)

  In kugui, PBS is used for the job scheduling system. In order to submit a batch job, a command ``qsub`` is invoked with the job script. There is no way to pass parameters to the script, and thus the name of the list file is fixed to ``list.dat``.

  .. code-block:: bash

      $ qsub job.sh


Check status
----------------------------------------------------------------

The status of execution of the tasks are written to log files. A tool named ``moller_status`` is provided to generate a summary of the status of each job from the log files. It is invoked by the following command in the directory where the batch job is executed:

.. code-block:: bash

  $ moller_status input.yaml list.dat

The command takes the job description file ``input.yaml`` and the list file ``list.dat`` as arguments. The list file may be omitted; in this case, the information of the jobs are extracted from the log files.

An example of the output is shown below:

.. literalinclude:: ../../../../tutorial/moller/reference/status.txt


where "o" corresponds to a task that has been completed successfully, "x" corresponds to a failed task, "-" corresponds to a skipped task because the previous task has been terminated with errors, and "." corresponds to a task yet unexecuted.


Retry/resume job
----------------------------------------------------------------

In case the job is terminated during the execution, the job may be resumed by submitting the batch job again with the same list file. The yet unexecuted jobs (as well as the unfinished jobs) will be run.


.. code-block:: bash

  $ sbatch job.sh list.dat

To retry the failed tasks, the batch job is submitted with ``--retry`` command line option.

.. code-block:: bash

  $ sbatch job.sh --retry list.dat

For kugui, to retry the failed tasks, the batch job script should be edited so that ``retry=0`` is changed to be ``retry=1``.

.. code-block:: bash

  $ qsub job.sh

Then, the batch job is submitted as above.

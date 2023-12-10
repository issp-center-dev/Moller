.. _sec-tutorial:

Tutorial
================================================================

The procedure to use the batch job script generator ``moller`` consists of the following steps:
First, a job description file is prepared that defines the tasks to be executed. Next, the program ``moller`` is to be run with the job description file, and a batch job script is generated. The script is then transferred to the target supercomputer system. A batch job is submitted with the script to perform calculations.
In this tutorial, we will explain the steps along a sample in ``docs/tutorial/moller``.

Prepare job description file
----------------------------------------------------------------

A job description file describes the content of calculations that are carried out in a batch job.
Here, a *batch job* is used for a set of instructions submitted to job schedulers running on supercomputer systems.
On the other hand, for the concurrent execution of programs that ``moller`` handles, we call a series of program executions performed for one set of parameters by a *job*. A job may consist of several contents that we call *tasks*. ``moller`` organizes job execution so that each task is run in parallel, and the synchronization between the jobs is taken at every start and end of the tasks.

.. only:: html

  .. figure:: ../../_static/task_view.png
     :alt: Tasks and jobs

     An example of tasks and jobs: Three jobs #1 ... #3 are carried out within a single batch job. Each job corresponds to different set of parameters. A job consists of 4 tasks. Each task is run in parallel among these three jobs.

.. only:: latex

  .. figure:: ../../_static/task_view.pdf
     :scale: 100%
     :alt: Tasks and jobs

     An example of tasks and jobs: Three jobs #1 ... #3 are carried out within a single batch job. Each job corresponds to different set of parameters. A job consists of 4 tasks. Each task is run in parallel among these three jobs.

An example of job description file is presented in the following. A job description file is in text-based YAML format. It contains parameters concerning the platform and the batch job, task descriptions, and pre/post-processes.

.. literalinclude:: ../../../../tutorial/moller/input.yaml

In the platform section, you can specify the type of platform on which to execute.
In this case, settings for the System B (ohtaka) are being made.
The prologue section describes the preprocessing of the batch job.
It details the common command line to be executed before running the task.
In the jobs section, the content of the task processing is described.
The series of tasks to be executed in the job are described in a table format,
with the task name as the key and the processing content as the value.
In this example, a task that first outputs "start..." is defined with the task name "start."
Here, it is set to "parallel = false." In this case, it will be executed as follows...
Next, a task that outputs "hello world." is defined with the task name "hello world." .
Here, since "parallel" is not set, it is executed as "parallel = true." .
In this case, it will be executed as follows...
Similarly, next, a task that outputs "hello world again." is defined with the task name "hello world again."
Finally, in the epilogue section, the post-processing of the batch job is described.
It details the common command line to be executed after running the task.
For more details on the specifications, please refer to the chapter :ref:`File Format <sec-fileformat>`.

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

The batch job is to be submitted to the job scheduler with the batch job script.
In ohtaka, slurm is used for the job scheduling system. In order to submit a batch job, a command ``sbatch`` is invoked with the job script as an argument.
Parameters can be passed to the script as additional arguments; the name of list file is specified as a parameter.

.. code-block:: bash

  $ sbatch job.sh list.dat

If the list file is not specified, ``list.dat`` is used by default.

Check status
----------------------------------------------------------------

The status of execution of the tasks are written to log files. A tool named ``moller_status`` is provided to generate a summary of the status of each job from the log files. It is invoked by the following command in the directory where the batch job is executed:

.. code-block:: bash

  $ moller_status input.yaml list.dat

The command takes the job description file ``input.yaml`` and the list file ``list.dat`` as arguments. The list file may be omitted; in this case, the information of the jobs are extracted from the log files.

An example of the output is shown below:

.. literalinclude:: ../../../../tutorial/moller/reference/status.txt


where "o" corresponds to a task that has been completed successfully, "x" corresponds to a failed task, "-" corresponds to a skipped task because the previous task has been terminated with errors, and "." corresponds to a task yet unexecuted.
In the above example, the all tasks have been completed successfully.

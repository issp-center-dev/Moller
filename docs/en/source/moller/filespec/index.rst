.. _sec-fileformat:

File format
================================================================

Job description file
----------------------------------------------------------------

A job description file contains configurations to generate a batch job script by ``moller``. It is prepared in text-based YAML format. This file consists of the following parts:

  1. General settings: specifies job names and output files.

  2. platform section: specifies the system on which batch jobs are executed, and the settings for the batch jobs.

  3. prologue and epilogue sections: specifies initial settings and finalization within the batch job.

  4. jobs section: specifies tasks to be carried out in the betch job script.

General settings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  ``name``

    specifies the name of the batch job. If it is not given, the job name is left unspecified. (Usually the name of the job script is used as the job name.)

  ``description``

    provides the description of the batch job. It is regarded as comments.

  ``output_file``

    specifies the output file name. When the output file is given by a command-line option, the command-line parameter is used. When none of them is specified, the result is written to the standard output.


platform
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  ``system``

    specifies the target system. At present, either ``ohtaka`` or ``kugui`` is accepted.

  ``queue``

    specifies the name of batch queue. The actual value depends on the target system.

  ``node``

    specifies the number of nodes to be used. It is given by an integer specifying the number of nodes, or a list of integers specifying ``[`` number of nodes, number of processes per node, number of cores per process ``]``. The accepted range of parameters depends on the system and queue settings.

  ``elapsed``

    specifies the elapsed time of the batch job in HH:MM:SS format.

prologue, epilogue
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
``prologue`` section specifies the commands to be run prior to executing the tasks. It is used, for example, to set environment variables of libraries and paths.
``epilogue`` section specifies the commands to be run after all tasks have been completed.

  ``code``

    specifies the content of the commands in the form of shell script. It is embedded in the batch job script, and executed within the batch job.

jobs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
``jobs`` section specifies a sequence of tasks in a table format, with the task names as keys and the contents as values.


  key

    name of task

  value

    a table that consists of the following items:

      ``description``

	provides the description of the task. It is regarded as comments.

      ``node``

	specifies the degree of parallelism in one of the following formats.
      
        - ``[`` number of processes, number of threads per process ``]``
        - ``[`` number of nodes, number of processes, number of threads per process ``]``
        - number of nodes

	When the number of nodes is specified, the specified number of nodes are exclusively assigned to a job. Otherwise, if the required number of cores for a job is smaller than the number of cores in a node, more than one job may be allocated in a single node. If a job uses more than one node, the required number of nodes are exclusively assigned.

      ``parallel``

	This parameter is set to ``true`` if the tasks of different jobs are executed in parallel. It is set to ``false`` if they are executed sequentially. The default value is ``true``.

      ``run``

	The content of the task is described in the form of shell script. The executions of MPI parallel programs or MPI/OpenMPI hybrid parallel programs are specified by

        .. code-block:: bash
      
            srun prog [arg1, ...]
	  
	where, in addition to the keyword ``srun``, ``mpirun`` or ``mpiexec`` is accepted. In the resulting job script, they are replaced by the command (e.g. ``srun`` or ``mpirun``) and the degree of parallelism specified by ``node`` parameter.

List file
----------------------------------------------------------------

This file contains a list of jobs. It is a text file with a job name in a line.

``moller`` assumes that a directory is assigned to each job, and the tasks of the job are executed within the directory. These directories are supposed to be located in the directory where the batch job is submitted. The name of the directory is associated with the name of the job.

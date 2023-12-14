# A sample calculation of Quantum ESPRESSO using *moller*

## What's this sample?

This is a trivial example of performing jobs in parallel using a job script generated with `moller`.
Each job executes band calculation of graphene by Quantum ESPRESSO. 
The configuration parameters are taken from a tutorial by Prof. Koretsune
[(http://www.cmpt.phys.tohoku.ac.jp/~koretsune/SATL_qe_tutorial/)](http://www.cmpt.phys.tohoku.ac.jp/~koretsune/SATL_qe_tutorial/).
The jobs are basically identical, with an option to let parameters vary over datasets.

## Preparation

Make sure that `moller` (HTP-tools) package is installed.
In this tutorial, the calculation will be performed using the supercomputer system `ohtaka` at ISSP.

## How to run

1. Prepare dataset

    Get the pseudo-potential data from the quantum espresso website and place it in the directory `pp`. A shell script is prepared for convenience.

    ```bash
    $ cd pp && sh ./fetch_pseudo.sh
    ```

    Copy the dataset with appropriate names. There is an option to modify the configuration parameters, e.g. to examine the parameter dependence for convergence.

    ```bash
    $ cp -r orig_dataset dataset_0001
      ...
    ```

2. Create list.dat

    Create a list of jobs as a list of data directories.

    ```bash
    $ ls -1d dataset_* > list.dat
    ```

3. Generate job script using `moller`

    Generate a job script from the job description file using `moller`, and store the script as a file named `job.sh`.

    ```bash
    $ moller input.yaml > job.sh
    ```

4. Run batch job

    Submit a batch job with the job list as an argument.

    ```bash
    $ sbatch job.sh list.dat
    ```

5. Check status

    The status of task execution will be summarized by `moller_status` program.

    ```bash
    $ moller_status input.yaml list.dat
    ```


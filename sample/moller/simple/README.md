# Trivial example for *moller* calculation

## What's this sample?

This is a trivial example to perform jobs in paralle using a job script generated with `moller`.
Each job executes two tasks that execute a simple echo program and writes the output to a file.
The jobs are basically identical, with an option to let parameters vary over datasets.

## Preparation

Make sure that `moller` (HTP-tools) package is installed.
In this tutorial, the calculation will be performed using the supercomputer system `ohtaka` at ISSP.

## How to run

1. Prepare dataset

    Run the script `make_inputs.sh` enclosed within this package.

    ```bash
    $ bash ./make_inputs.sh
    ```

    A directory `output` is created, and a set of directories `dataset-0001` ... `dataset-0020` will be generated within `output`. They correspond to the dataset. A list of the dataset is written to a file `list.dat`.

2. Generate job script using `moller`

    Generate a job script from the job description file using `moller`, and store the script as a file named `job.sh`.

    ```bash
    $ moller -o job.sh input.yaml
    ```

    Then, copy `job.sh` in the `output` directory, and change directory to `output`.

3. Run batch job

    Submit a batch job with the job list as an argument.

    ```bash
    $ sbatch job.sh list.dat
    ```

4. Check status

    The status of task execution will be summarized by `moller_status` program.

    ```bash
    $ moller_status input.yaml list.dat
    ```

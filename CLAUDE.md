# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

moller (part of the ISSP HTP-Tools package) generates batch job scripts for supercomputers and clusters. It reads a YAML job description and emits a single bash script that runs a chain of tasks over many dataset directories in parallel using GNU Parallel, with per-task status logging, resume/retry support, and dependency skipping between tasks.

## Commands

```bash
# Install (poetry-core build; editable install works too)
python3 -m pip install .

# Generate a job script from a YAML description (writes to stdout without -o)
moller input.yaml -o job.sh

# Show job status from GNU Parallel joblogs (stat_<task>.dat) in the run directory
moller_status input.yaml list.dat            # optional: --csv/--html, --failed/--ok/--yet/...

# Build docs (Sphinx, both languages; requires sphinx installed)
make -C docs/en html
make -C docs/ja html
```

There is no pytest suite and no linter configured. `tests/moller/` is an on-cluster integration test: `mkdataset.sh` creates dataset directories and `list.dat`, then the moller-generated `job.sh` is submitted to run `moller_test.py` (an MPI program with configurable sleep/failure rate) — it can only be validated on a machine with a scheduler and mpi4py. Sample YAML inputs in `sample/moller/` and `tests/moller/input.yaml` are the reference for input-format behavior; `reference/` subdirectories hold expected status output.

Versioning: `src/moller/__init__.py` (`__version__`) and `pyproject.toml` must be kept in sync. Development flows through the `develop` branch and merges to `main`; docs are auto-built and deployed to gh-pages by `.github/workflows/deploy_docs.yml`.

## Architecture

Two entry points (declared in pyproject.toml):

- `moller.main:main` — script generation. `ScriptGenerator` parses the YAML and assembles an ordered task list: prologue → bash function definitions → logfile check → jobs (in YAML order) → epilogue. Each entry in `jobs:` becomes either a `TaskParallel` (default) or a `TaskSerial` (`parallel: false`). A `TaskParallel` is emitted as a bash function `task_<name>` invoked through GNU Parallel over the work items piped in from `list.dat`, logging to `stat_<name>.dat`.
- `moller.moller_status:main` — status reporting. Re-parses the same input YAML to discover the parallel tasks and their `stat_<task>.dat` joblogs, then renders a job × task table (o = ok, x = failed, `-` = skipped, `.` = not run) as text/csv/html with filters.

Platform abstraction (`src/moller/platform/`):

- `base.py` defines the `Platform` base class plus a factory registry: `register_platform(name, cls)` / `create_platform(name, info)`. Each concrete platform module calls `register_platform(...)` at import time, and `platform/__init__.py` imports them all — a new platform is not usable until it is imported there.
- Scheduler families are the mid-layer bases: `base_slurm.py` (Slurm/#SBATCH), `base_pbs.py` (PBS/#PBS), `base_default.py` (plain bash, no scheduler). Concrete platforms are thin subclasses: `ohtaka` (Slurm, ISSP), `kugui` (PBS, ISSP), `pbs`, `default` — typically overriding only `parallel_command()` and defaults.
- `function.py` holds the scheduler-independent bash helpers embedded into every generated script (`run_parallel`, `_is_ready`, retry/ulimit handling, DEBUG); scheduler-specific helpers (`_setup_taskenv`, `_setup_run_parallel`, `_find_multiplicity`) are defined in the `base_slurm`/`base_pbs`/`base_default` classes and assembled by each base's `generate_function()`.

Key generation mechanics to preserve when editing:

- In each parallel task's `run:` block, any line containing `srun`, `mpirun`, or `mpiexec` has that word substituted with the platform-specific parallel command (e.g. ohtaka: `srun --exclusive --mem-per-cpu=1840 -N $_nn -n $_np -c $_nc`). The `node:` spec (scalar or 1–3 element list) is normalized to `[nodes, procs, cores]` and passed as the `$_sig` signature to `run_parallel`, which computes how many work items run concurrently.
- Task chaining: consecutive parallel tasks are linked via `prev_log_file` — the generated `_is_ready` check reads the previous task's joblog and exits 255 for work items whose previous step failed, which `moller_status` reports as skipped (`-`). Serial tasks do not participate in this chain.
- Joblog format is GNU Parallel's tab-separated joblog; `moller_status.read_joblog_file` parses the `Command` field positionally (4 fields = single parallel, 7 = nested parallel) — changes to the `run_parallel` invocation signature in generated scripts must keep that parser in sync.

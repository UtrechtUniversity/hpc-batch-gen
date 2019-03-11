"""
Module for testing the batchgen package as a whole.

@author Raoul Schram
"""

import os
import configparser as cp

from batchgen import batch_from_files, batch_from_strings
from batchgen.base import _read_pre_post_file
from batchgen.util import batch_dir


def _config_slurm_local():
    config = """[BACKEND]
backend = slurm_lisa
[BATCH_OPTIONS]
clock_wall_time = 02:00:00
num_cores = 16
num_tasks_per_node = 30
num_cores_simul = 15
job_name = asr_sim
base_dir = .
tmp_dir = ${TMP_DIR}/asr
output_dir = sum_output
send_mail = True
"""
    return config


def _config_slurm_remote():
    config = """
[CONNECTION]
remote_dir = batchgen/samples
server = lisa.surfsara.nl
"""
    return _config_slurm_local()+config


def _config_parallel():
    config = """[BACKEND]
backend = parallel
[BATCH_OPTIONS]
job_name = my_test
tmp_dir = tmp_sum
base_dir = .
output_dir = sum_output
"""
    return config


def _pre_post_input():
    pp = """\
## PRE_COMMANDS ##

if [ "${backend}" == "slurm_lisa" ]; then
    module load eb
    module load Python/3.6.1-intel-2016b
fi

mkdir -p ${tmp_dir}
cd ${base_dir}

## POST_COMMANDS ##

mkdir -p ${output_dir}
cp ${tmp_dir}/sum*.dat ${output_dir}
"""
    return pp


def _commands():
    command = """./sum.sh 0 ${tmp_dir}
./sum.sh 1 ${tmp_dir}
./sum.sh 10 ${tmp_dir}
./sum.sh 12 ${tmp_dir}
./sum.sh 234 ${tmp_dir}
./sum.sh 5293 ${tmp_dir}
./sum.sh 529384 ${tmp_dir}
./sum.sh 1782641 ${tmp_dir}
./sum.sh 128342 ${tmp_dir}
./sum.sh 12984715 ${tmp_dir}
./sum.sh 712948 ${tmp_dir}
./sum.sh 452489 ${tmp_dir}
./sum.sh 1982641 ${tmp_dir}
"""
    return command


def _batch_parallel(tdir):
    batch_content = """\

#!/bin/bash


if [ "parallel" == "slurm_lisa" ]; then
    module load eb
    module load Python/3.6.1-intel-2016b
fi

mkdir -p tmp_sum
cd .


parallel < {tdir}/batch.parallel/\
my_test/commands.sh

mkdir -p sum_output
cp tmp_sum/sum*.dat sum_output

""".format(tdir=tdir)
    return batch_content


def _batch_slurm_local():
    batch_content = """\

#!/bin/bash
#SBATCH -t 02:00:00
#SBATCH --tasks-per-node=13
#SBATCH -J asr_sim


if [ "slurm_lisa" == "slurm_lisa" ]; then
    module load eb
    module load Python/3.6.1-intel-2016b
fi

mkdir -p ${TMP_DIR}/asr
cd .


parallel -j 15 << EOF_PARALLEL
./sum.sh 0 ${TMP_DIR}/asr &> /dev/null
./sum.sh 1 ${TMP_DIR}/asr &> /dev/null
./sum.sh 10 ${TMP_DIR}/asr &> /dev/null
./sum.sh 12 ${TMP_DIR}/asr &> /dev/null
./sum.sh 234 ${TMP_DIR}/asr &> /dev/null
./sum.sh 5293 ${TMP_DIR}/asr &> /dev/null
./sum.sh 529384 ${TMP_DIR}/asr &> /dev/null
./sum.sh 1782641 ${TMP_DIR}/asr &> /dev/null
./sum.sh 128342 ${TMP_DIR}/asr &> /dev/null
./sum.sh 12984715 ${TMP_DIR}/asr &> /dev/null
./sum.sh 712948 ${TMP_DIR}/asr &> /dev/null
./sum.sh 452489 ${TMP_DIR}/asr &> /dev/null
./sum.sh 1982641 ${TMP_DIR}/asr &> /dev/null
EOF_PARALLEL


mkdir -p sum_output
cp ${TMP_DIR}/asr/sum*.dat sum_output


if [ "True" == "True" ]; then
    echo "Job $SLURM_JOBID ended at `date`" | mail $USER -s \
"Job: asr_sim/0 ($SLURM_JOBID)"
fi
date
"""
    return batch_content


def results_tester(tdir, config_file, batch_expected):
    """ From a directory/configuration file and some expected result,
        see if everything is as expected. """

    config = cp.ConfigParser()
    config.read(config_file)

    job_name = config.get("BATCH_OPTIONS", "job_name")
    backend = config.get("BACKEND", "backend")
    remote = config.has_section("CONNECTION")
    abs_batch_dir = batch_dir(backend=backend, job_name=job_name,
                              remote=remote)
    if backend == "slurm_lisa":
        batch_file = os.path.join(tdir, abs_batch_dir, "batch0.sh")
    else:
        batch_file = os.path.join(tdir, abs_batch_dir, "batch.sh")

    with open(batch_file, "r") as f:
        batch_content = f.read()

    assert batch_content == batch_expected


def file_test(command_string, config, pre_post_input, batch_expected, tdir,
              pp_in_config, force_clear=False):
    """ Using the CLI/file API batch creation, test if results match expectations.
    """
    tdir = str(tdir)
    pre_post_file = "pp_sum.sh"
    config_file = os.path.join(tdir, "config.ini")
    pp_file = os.path.join(tdir, pre_post_file)
    command_file = os.path.join(tdir, "command.sh")
    os.chdir(tdir)

    # Add the pre_post_file to the options in the configuration file.
    if pp_in_config:
        config += "pre_post_file = " + pre_post_file + "\n"
        pre_post_file = None

    with open(config_file, "w") as f:
        f.write(config)
    with open(command_file, "w") as f:
        f.write(command_string)
    with open(pp_file, "w") as f:
        f.write(pre_post_input)

    batch_from_files(command_file, config_file, pre_post_file=pre_post_file,
                     force_clear=force_clear)

    results_tester(tdir, config_file, batch_expected)


def string_test(command_string, config, pre_post_input, batch_expected, tdir,
                force_clear=False):
    """ Using the string API batch creation, test if results match expectations.
    """
    tdir = str(tdir)
    config_file = os.path.join(tdir, "config.ini")
    pp_file = os.path.join(tdir, "pp_sum.sh")
    os.chdir(tdir)

    with open(config_file, "w") as f:
        f.write(config)
    with open(pp_file, "w") as f:
        f.write(pre_post_input)

    pre_string, post_string = _read_pre_post_file(pp_file)

    batch_from_strings(command_string, config_file, pre_string, post_string,
                       force_clear=force_clear)

    results_tester(tdir, config_file, batch_expected)


def test_parallel_file(tmpdir):
    """ Test the parallel backend using different methods/settings.
    """
    config = _config_parallel()
    batch_expected = _batch_parallel(tmpdir)
    pre_post_input = _pre_post_input()
    command_string = _commands()
    file_test(command_string, config, pre_post_input, batch_expected, tmpdir,
              True)
    file_test(command_string, config, pre_post_input, batch_expected, tmpdir,
              False, True)
    string_test(command_string, config, pre_post_input, batch_expected, tmpdir,
                True)


def test_slurm_local_file(tmpdir):
    """ Test the SLURM/Lisa backend with different methods/settings.
    """
    config = _config_slurm_local()
    batch_expected = _batch_slurm_local()
    pre_post_input = _pre_post_input()
    command_string = _commands()
    file_test(command_string, config, pre_post_input, batch_expected, tmpdir,
              True)
    file_test(command_string, config, pre_post_input, batch_expected, tmpdir,
              False, True)
    string_test(command_string, config, pre_post_input, batch_expected, tmpdir,
                True)

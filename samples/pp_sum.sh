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

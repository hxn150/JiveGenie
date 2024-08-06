# Setup everything for this repository
# Modified setup_conda.sh from Anyloc/Anyloc repository: https://github.com/AnyLoc/AnyLoc/blob/main/setup_conda.sh

readonly ARGS="$@"  # Reset using https://stackoverflow.com/a/4827707
readonly PROGNAME=$(basename $0)
readonly PROGPATH=$(realpath $(dirname $0))
export CUDA_HOME=/usr/local/cuda

echo $CUDA_HOME

# Internal variables
env_name="jiveGenie"   # Name of the environment
exec_name="conda"           # Executable
dry_run="false"     # 'true' or 'false'
ask_prompts="true"  # 'true' or 'false'
dev_tools="false"   # 'true' or 'false'
warn_exit="true"    # 'true' or 'false'

# Output formatting
debug_msg_fmt="\e[2;90m"
info_msg_fmt="\e[1;37m"
warn_msg_fmt="\e[1;35m"
fatal_msg_fmt="\e[2;31m"
command_msg_fmt="\e[0;36m"
# Wrapper printing functions
echo_debug () {
    echo -ne $debug_msg_fmt
    echo $@
    echo -ne "\e[0m"
}
echo_info () {
    echo -ne $info_msg_fmt
    echo $@
    echo -ne "\e[0m"
}
echo_warn () {
    echo -ne $warn_msg_fmt
    echo $@
    echo -ne "\e[0m"
}
echo_fatal () {
    echo -ne $fatal_msg_fmt
    echo $@
    echo -ne "\e[0m"
}
echo_command () {
    echo -ne $command_msg_fmt
    echo $@
    echo -ne "\e[0m"
}
# Installer functions
function run_command() {
    echo_command $@
    if [ $dry_run == "true" ]; then
        echo_debug "Dry run, not running command..."
    else
        $@
    fi
}

function conda_install() {
    run_command $exec_name install -y --freeze-installed --no-update-deps $@
    ec=$?
    if [[ $ec -gt 0 ]]; then
        echo_warn "Could not install '$@', maybe try though conda_raw_install"
        if [[ $warn_exit == "true" ]]; then
            exit $ec
        else
            echo_debug "Exit on warning not set, continuing..."
        fi
    fi
}
function conda_raw_install() {
    run_command $exec_name install -y $@
}
function pip_install() {
    run_command pip install --upgrade $@
}

# Ensure installation can happen
if [ -x "$(command -v mamba)" ]; then   # If mamba found
    echo_debug "Found mamba"
    exec_name="mamba"
elif [ -x "$(command -v conda)" ]; then # If conda found
    echo_debug "Found conda (couldn't find mamba)"
    exec_name="conda"
else
    echo_fatal "Could not find mamba or conda! Install, source, and \
            activate it."
    exit 127
fi


function parse_options() {
    # Set passed arguments
    set -- $ARGS
    pos=1
    while (( "$#" )); do
        arg=$1
        shift
        case "$arg" in
            # Conda installation to use
            "--conda" | "-c")
                ci=$1
                shift
                echo_debug "Using $ci (for anaconda base)"
                exec_name=$ci
                ;;
            # Developer install options
            "--dev" | "-d")
                echo_debug "Installing documentation and packaging tools"
                dev_tools="true"
                ;;
            # Dry run
            "--dry-run")
                echo_debug "Dry run mode enabled"
                dry_run="true"
                ;;
            # Environment name
            "--env-name" | "-e")
                en=$1
                shift
                echo_debug "Using environment $en"
                env_name=$en
                ;;
            # No exit on warning
            "--no-exit-on-warn")
                echo_debug "No exit on warning set"
                warn_exit="false"
                ;;
            # No prompt
            "--no-prompt" | "-n")
                echo_debug "Not showing prompts (no Enter needed)"
                ask_prompts="false"
                ;;
            *)
                if [ $pos -eq 1 ]; then # Environment name
                    echo_debug "Using environment $arg"
                    env_name=$arg
                else
                    echo_fatal "Unrecognized option: $arg"
                    echo_debug "Run 'bash $PROGNAME --help' for usage"
                    exit 1
                fi 
        esac
        pos=$((pos + 1))
    done
}

# ====== Main program entrypoint ======
parse_options
if [ -x "$(command -v $exec_name)" ]; then
    echo_info "Using $exec_name (for base anaconda)"
else
    echo_fatal "Could not find $exec_name! Install, source, and \
            activate it."
    exit 1
fi

# if [ "$CONDA_DEFAULT_ENV" != "$env_name" ]; then
#     echo_fatal "Wrong environment activated. Activate $env_name"
#     exit 1
# fi

# Confirm environment
echo_info "Using environment: $CONDA_DEFAULT_ENV"
echo_info "Python: $(which python)"
echo_debug "Python version: $(python --version)"
echo_info "Pip: $(which pip)"
echo_debug "Pip version: $(pip --version)"
if [ $ask_prompts == "true" ]; then
    read -p "Continue? [Ctrl-C to exit, enter to continue] "
elif [ $ask_prompts == "false" ]; then
    echo_info "Continuing..."
fi

# Install packages
start_time=$(date)
start_time_secs=$SECONDS
echo_debug "---- Start time: $start_time ----"
# Core packages using conda_install and conda_raw_install
echo_info "------ Installing core packages ------"

pip_install flask flask_cors
pip_install python-dotenv
pip_install wandb
pip_install p_tqdm
pip_install moviepy
sudo apt-get install libsndfile1

# install jukemirlib and EDGE dependencies
echo_info "------ Installing EDGE packages ------"
pip_install git+https://github.com/rodrigo-castellon/jukemirlib.git
cd backend/EDGE
cd ../..


# install pytorch3d
echo_info "------ Installing pytorch3d packages ------"
conda_raw_install -c conda_forge ffmpeg
conda_install -c fvcore -c iopath -c conda-forge fvcore iopath -y
conda_install -c bottler nvidiacub -y
conda_install -c pytorch3d pytorch3d

# install mmhuman3d
echo_info "------ Installing mmhuman3d packages ------"

pip_install "mmcv-full>=1.3.17,<1.6.0" -f https://download.openmmlab.com/mmcv/dist/cu121/torch2.4.0/index.html
git clone https://github.com/open-mmlab/mmhuman3d.git


# Installation ended
end_time=$(date)
end_time_secs=$SECONDS
echo_debug "---- End time: $end_time ----"
# dur=$(echo $(date -d "$end_time" +%s) - $(date -d "$start_time" +%s) | bc -l)
dur=$(( $end_time_secs - $start_time_secs ))
_d=$(( dur/3600/24 ))   # Days!
echo_info "---- Environment setup took (d-HH:MM:SS): \
        $_d-`date -d@$dur -u +%H:%M:%S` ----"
echo_info "----- Environment $CONDA_DEFAULT_ENV has been setup -----"
echo_debug "Starting time: $start_time"
echo_debug "Ending time: $end_time"
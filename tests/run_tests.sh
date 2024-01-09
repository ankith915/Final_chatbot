#!/bin/sh
export DB_CONFIG=configs/db_config.json
export LOGLEVEL=INFO

# Set default values
llm_service="all"
schema="all"
use_wandb="true"

# Check if llm_service argument is provided
if [ "$#" -ge 1 ]; then
    llm_service="$1"
fi

# Check if schema argument is provided
if [ "$#" -ge 2 ]; then
    schema="$2"
fi

# Check if use_wandb argument is provided
if [ "$#" -ge 3 ]; then
    use_wandb="$3"
fi

# Define the mapping of Python script names to JSON config file names
script_mapping=(
    "test_azure_gpt35_turbo_instruct.py ../configs/azure_llm_config.json"
    "test_openai_gpt35-turbo.py ../configs/openai_gpt3.5-turbo_config.json"
    "test_openai_gpt4.py ../configs/openai_gpt4_config.json"
    "test_gcp_text-bison.py ../configs/gcp_text-bison_config.json"
)

# Function to execute a service
execute_service() {
    local script_and_config=($1)
    local service="${script_and_config[0]}"
    local config_file="${script_and_config[1]}"

    # Export the path to the config file as an environment variable
    export LLM_CONFIG="$config_file"

    if [ "$use_wandb" = "true" ]; then
        python "$service" --schema "$schema"
    else
        python "$service" --schema "$schema" --no-wandb
    fi

    # Unset the environment variable after the Python script execution
    unset CONFIG_FILE_PATH
}

# Check the value of llm_service and execute the corresponding Python script(s)
case "$llm_service" in
    "azure_gpt35")
        execute_service "${script_mapping[0]}"
        ;;
    "openai_gpt35")
        execute_service "${script_mapping[1]}"
        ;;
    "openai_gpt4")
        execute_service "${script_mapping[2]}"
        ;;
    "gcp_textbison")
        execute_service "${script_mapping[3]}"
        ;;
    "all")
        echo "Executing all services..."
        for service_script in "${!script_mapping[@]}"; do
            execute_service "$service_script"
        done
        ;;
    *)
        echo "Unknown llm_service: $llm_service"
        exit 1
        ;;
esac



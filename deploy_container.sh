#!/bin/bash
set -E

# Set colours
RED=$(tput setaf 1)
GREEN=$(tput setaf 2)
PURPLE=$(tput setaf 6)
RESET=$(tput sgr0)

# Help/usage
function print_help {
    echo ${PURPLE}
    cat <<EOH
Usage: $(basename "$0") --owm KEY --telegram KEY --port PORT

Pay attention instance must have public ip and open https port!

Required options:
  --owm          STR     OWM API key
  --telegram     STR     Telegram API key
  --port         INT     HTTPS port
EOH
    exit 1
    echo ${RESET}
}

# Print error and exit with fault code 2
function stderr {
    printf 'Error:\t%s\n\n' "$1" >&2
    print_help
    exit 2
}

# Extract the value from an argument, and exit with error if no value is present
function argval() {
    [[ -z $2 || $2 =~ ^-- ]] && stderr "Missing value for argument $1!"
}

# Check required arguments provided, parse all arguments passed to the script
if (($#)); then
    req_args=('--owm' '--telegram' '--port')
    for arg in "${req_args[@]}"; do
        for parg in ${@}; do
            if [[ $parg == '-h' || $parg == '--help' ]]; then
                print_help
            else
                [[ ! ${@} =~ $arg ]] && stderr "Missing required argument $arg!"
            fi
        done
    done
    while [[ ${#} -gt 0 ]]; do
        ARG=$1
        shift
        case $ARG in
            -h|--help)
                print_help
                ;;
            --owm)
                argval "$ARG" "$1"; OWM_KEY=$1; shift
                ;;
            --telegram)
                argval "$ARG" "$1"; TELEBOT_KEY=$1; shift
                ;;
            --port)
                argval "$ARG" "$1"; HTTPS_PORT=$1; shift
                ;;
        esac
    done
else
    stderr 'No arguments supplied!'
fi

# Main block
if [[ $(uname -s) -eq 'Linux' ]]; then
    if [[ $EUID -ne 0 ]]; then
        echo "${RED}Please run as root.${RESET}"
        exit
    else
        if [[ $(compgen -c | grep -x 'docker') ]]; then
            SERVER_VERSION=$(docker version -f "{{.Server.Version}}" | cut -d'.' -f 1 )
            if [[ $SERVER_VERSION -ge 17 ]]; then
                if [[ -f $(find . -maxdepth 1 -name "Dockerfile") ]] && [[ -f $(find . -maxdepth 1 -name "*.py") ]]; then
                    docker_tag=$(tr -dc a-z0-9 </dev/urandom | head -c 4; echo '')
                    docker build --build-arg OWN_KEY="$OWM_KEY" --build-arg TELEBOT_KEY="$TELEBOT_KEY" --build-arg WEBHOOK_HOST="$(curl -s ifconfig.co)" --build-arg WEBHOOK_PORT="$HTTPS_PORT" -t "skbweatherbot:$docker_tag" . > /dev/null 2>&1
                    if [[ -n $(docker images "skbweatherbot:$docker_tag" -q) ]]; then
                        echo "${GREEN}Bot image skbweatherbot:$docker_tag built successfully${RESET}"
                        docker run -d --restart=always --name skbweatherbot -p "$HTTPS_PORT:$HTTPS_PORT" "$(docker images skbweatherbot:"$docker_tag" -q)" > /dev/null 2>&1
                        sleep 5
                        if [[ $(docker ps -a | grep skbweatherbot | awk '{print $8}') == 'Up' ]]; then
                            echo "${GREEN}Bot container deployed successfully${RESET}"
                        else
                            echo "${RED}Bot container deployed unsuccessfully.${RESET}"
                            exit
                        fi
                    else
                        echo "${RED}Bot image built unsuccessfully.${RESET}"
                        exit
                    fi
                else
                    echo "${RED}Either Dockerfile or skbweatherbot is not exist in current directory.${RESET}"
                    exit
                fi
            else
                echo "${RED}Docker version is $(docker version -f "{{.Server.Version}}"), less than 17.05.0 can't continue.${RESET}"
                exit
            fi
        else
            echo "${RED}Docker not installed. Please install docker and re-run script.${RESET}"
            exit
        fi
    fi
else
    echo "${RED}Your platform ($(uname -a)) is not supported.${RESET}"
    exit 1
fi
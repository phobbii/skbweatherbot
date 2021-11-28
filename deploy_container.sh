#!/bin/bash
set -E

# Set colours
RED=`tput setaf 1`
GREEN=`tput setaf 2`
PURPLE=`tput setaf 6`
RESET=`tput sgr0`

# Ensure we can exit if a subshell returns error
stderr() {
    echo "${GREEN}${1}${RESET}" >&2
}

# Print error and exit with fault code 2
error() {
    stderr "${RED}ERROR: ${1}${RESET}"
    exit 2
}

# Print if debug is enabled
debug() {
        [[ "${DEBUG}" == ${TRUE} ]] && stderr "DEBUG: ${1}"
}

# Extract the value from an argument, and exit with error if no value is present
argval() {
        debug "${1} ${2}"
        [[ -z "${2}" || "${2}" =~ ^-- ]] && error "Missing value for argument: ${1}"
        echo "${2}"
}

# Help/usage
if [[ "${1}" == '-h' || "${1}" == '--help' ]]; then
    echo ${PURPLE}
    cat <<EOH
Usage: $(basename $0) --owm KEY --telegram KEY --port PORT

Pay attention instance must have public ip and open https port!

Required options:
  --owm STR          OWM API key
  --telegram STR     Telegram API key
  --port INT         HTTPS port
EOH
    exit 0
    echo ${RESET}
fi

# Parse all arguments passed to the script
while [[ "${#}" -gt 0 ]]; do
        ARG="${1}"
        shift
        case "${ARG}" in
                --owm)
                        OWM_KEY=$(argval "${ARG}" "${1}"); shift
                        ;;
                --telegram)
                        TELEBOT_KEY=$(argval "${ARG}" "${1}"); shift
                        ;;
                --port)
                        HTTPS_PORT=$(argval "${ARG}" "${1}"); shift
                        ;;
        esac
done

# Check if we got the required values
[[ -z "${OWM_KEY}" ]] && error "Missing argument: --owm"
[[ -z "${TELEBOT_KEY}" ]] && error "Missing argument: --telegram"
[[ -z "${HTTPS_PORT}" ]] && error "Missing argument: --port"
[[ ! "${HTTPS_PORT}" =~ ^[0-9]+$ || "${#HTTPS_PORT}" -lt 3 || "${#HTTPS_PORT}" -gt 5 ]] && error "Invalid port: ${HTTPS_PORT}"

# Main block
if [[ $(uname -s) -eq "Linux" ]]; then
    if [[ $EUID -ne 0 ]]; then
        echo "${RED}Please run as root.${RESET}"
        exit
    else
        if [[ $(compgen -c | grep -x "docker") ]]; then
            SERVER_VERSION=$(docker version -f "{{.Server.Version}}")
            SERVER_VERSION_MAJOR=$(echo "$SERVER_VERSION"| cut -d'.' -f 1)
            SERVER_VERSION_MINOR=$(echo "$SERVER_VERSION"| cut -d'.' -f 2)
            SERVER_VERSION_BUILD=$(echo "$SERVER_VERSION"| cut -d'.' -f 3)
            if [ "${SERVER_VERSION_MAJOR}" -ge 17 ] && [ "${SERVER_VERSION_MINOR}" -ge 5 ] && [ "${SERVER_VERSION_BUILD}" -ge 0 ]; then
                if [[ -f $(find . -maxdepth 1 -name "Dockerfile") ]] && [[ -f $(find . -maxdepth 1 -name "*.py") ]]; then
                    docker build --build-arg OWN_KEY="${OWM_KEY}" --build-arg TELEBOT_KEY="${TELEBOT_KEY}" --build-arg WEBHOOK_HOST="$(curl -s ifconfig.co)" --build-arg WEBHOOK_PORT="${HTTPS_PORT}" -t skbweatherbot . > /dev/null 2>&1
                    if [[ -n $(docker images | grep "skbweatherbot" | awk '{print $3}') ]]; then
                        echo "${GREEN}Bot image built successfully${RESET}"
                        docker run -d --restart=always --name skbweatherbot -p $HTTPS_PORT:$HTTPS_PORT $(docker images | grep "skbweatherbot" | awk '{print $3}') > /dev/null 2>&1
                        if [[ $(docker ps -a | grep skbweatherbot | awk '{print $8}') == "Up" ]]; then
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
                echo "${RED}Docker version less than 17.05.0 can't continue.${RESET}"
                exit
        else
            echo "${RED}Docker not installed. Please install docker and re-run script.${RESET}"
            exit
        fi
    fi
else
    echo "${RED}Your platform ($(uname -a)) is not supported.${RESET}"
    exit 1
fi
#!/bin/bash
set -e

RED=$(tput setaf 1)
GREEN=$(tput setaf 2)
PURPLE=$(tput setaf 6)
RESET=$(tput sgr0)

function print_help(){
    echo "${PURPLE}"
    cat <<EOH
Usage: $(basename "$0") --owm KEY --telegram KEY --port PORT

Deploy the modular weather bot in a Docker container.
Instance must have a public IP and open HTTPS port.

Required options:
  --owm          STR     OpenWeatherMap API key
  --telegram     STR     Telegram Bot API token
  --port         INT     HTTPS port (e.g., 8443)

Example:
  $(basename "$0") --owm abc123 --telegram 123456:ABC-DEF --port 8443
EOH
    echo "${RESET}"
    exit 1
}

function stderr(){
    printf "${RED}Error: %s\n\n${RESET}" "$1" >&2
    print_help
}

function validate_arg(){
    [[ -z $2 || $2 =~ ^-- ]] && stderr "Missing value for argument $1"
}

function check_provided_args(){
    [[ $# -eq 0 ]] && stderr "No arguments supplied"
    
    req_args=('--owm' '--telegram' '--port')
    for arg in "${req_args[@]}"; do
        [[ ! " $* " =~ " $arg " ]] && stderr "Missing required argument $arg"
    done
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help) print_help ;;
            --owm) validate_arg "$1" "$2"; OWM_KEY=$2; shift 2 ;;
            --telegram) validate_arg "$1" "$2"; TELEBOT_KEY=$2; shift 2 ;;
            --port) validate_arg "$1" "$2"; HTTPS_PORT=$2; shift 2 ;;
            *) stderr "Unknown argument: $1" ;;
        esac
    done
}

check_provided_args "$@"

[[ $(uname -s) != "Linux" ]] && { echo "${RED}Only Linux is supported${RESET}"; exit 1; }
[[ $EUID -ne 0 ]] && { echo "${RED}Please run as root${RESET}"; exit 1; }

command -v docker >/dev/null 2>&1 || { echo "${RED}Docker not installed${RESET}"; exit 1; }

SERVER_VERSION=$(docker version -f "{{.Server.Version}}" 2>/dev/null | cut -d'.' -f1)
[[ $SERVER_VERSION -lt 17 ]] && { echo "${RED}Docker version must be >= 17.05${RESET}"; exit 1; }

[[ ! -f Dockerfile ]] && { echo "${RED}Dockerfile not found in current directory${RESET}"; exit 1; }
[[ ! -d src ]] && { echo "${RED}src/ directory not found in current directory${RESET}"; exit 1; }
[[ ! -f src/bot.py ]] && { echo "${RED}src/bot.py not found${RESET}"; exit 1; }

PUBLIC_IP=$(curl -s --max-time 5 ifconfig.co || curl -s --max-time 5 ident.me || echo "")
[[ -z $PUBLIC_IP ]] && { echo "${RED}Failed to detect public IP${RESET}"; exit 1; }

echo "${GREEN}Building bot image...${RESET}"
DOCKER_TAG=$(tr -dc a-z0-9 </dev/urandom | head -c 6)

docker build \
    --build-arg OWM_KEY="$OWM_KEY" \
    --build-arg TELEBOT_KEY="$TELEBOT_KEY" \
    --build-arg WEBHOOK_HOST="$PUBLIC_IP" \
    --build-arg WEBHOOK_PORT="$HTTPS_PORT" \
    -t "skbweatherbot:$DOCKER_TAG" .

[[ -z $(docker images "skbweatherbot:$DOCKER_TAG" -q) ]] && { echo "${RED}Build failed${RESET}"; exit 1; }

echo "${GREEN}Image skbweatherbot:$DOCKER_TAG built successfully${RESET}"

docker stop skbweatherbot 2>/dev/null || true
docker rm skbweatherbot 2>/dev/null || true

echo "${GREEN}Starting container...${RESET}"
docker run -d \
    --restart=always \
    --name skbweatherbot \
    -p "$HTTPS_PORT:$HTTPS_PORT" \
    "skbweatherbot:$DOCKER_TAG"

sleep 5

if docker ps | grep -q skbweatherbot; then
    echo "${GREEN}Bot deployed successfully${RESET}"
    echo "${GREEN}Container: skbweatherbot${RESET}"
    echo "${GREEN}Webhook: https://$PUBLIC_IP:$HTTPS_PORT${RESET}"
else
    echo "${RED}Deployment failed. Check logs: docker logs skbweatherbot${RESET}"
    exit 1
fi

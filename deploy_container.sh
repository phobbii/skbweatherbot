#!/bin/sh

RED=$(tput setaf 1 2>/dev/null || echo "")
GREEN=$(tput setaf 2 2>/dev/null || echo "")
PURPLE=$(tput setaf 6 2>/dev/null || echo "")
RESET=$(tput sgr0 2>/dev/null || echo "")

print_help() {
    printf "%s" "${PURPLE}"
    cat <<EOH
Usage: $(basename "$0") --owm KEY --telegram KEY --port PORT

Deploy the modular weather bot in a Docker container.
Instance must have a public IP and open HTTPS port.

Required options:
  --owm          STR     OpenWeatherMap API key
  --telegram     STR     Telegram Bot API token
  --public_ip    STR     Public IP
  --port         INT     Port (e.g., 8443)

Example:
  $(basename "$0") --owm "abc123" --telegram "123456:ABC-DEF" --public_ip "198.51.100.42" --port 8443
EOH
    printf "%s" "${RESET}"
    exit 1
}

stderr() {
    printf "${RED}Error: %s\n\n${RESET}" "$1" >&2
    print_help
}

validate_arg() {
    case "$2" in
        ''|--*) stderr "Missing value for argument $1" ;;
    esac
}

check_provided_args() {
    [ $# -eq 0 ] && stderr "No arguments supplied"
    
    has_owm=0 has_telegram=0 has_public_ip=0 has_port=0
    for arg in "$@"; do
        case "$arg" in
            --owm) has_owm=1 ;;
            --telegram) has_telegram=1 ;;
            --public_ip) has_public_ip=1 ;;
            --port) has_port=1 ;;
        esac
    done
    [ $has_owm -eq 0 ] && stderr "Missing required argument --owm"
    [ $has_telegram -eq 0 ] && stderr "Missing required argument --telegram"
    [ $has_public_ip -eq 0 ] && stderr "Missing required argument --public_ip"
    [ $has_port -eq 0 ] && stderr "Missing required argument --port"
    
    while [ $# -gt 0 ]; do
        case $1 in
            -h|--help) print_help ;;
            --owm) validate_arg "$1" "$2"; OWM_KEY=$2; shift 2 ;;
            --telegram) validate_arg "$1" "$2"; TELEBOT_KEY=$2; shift 2 ;;
            --public_ip) validate_arg "$1" "$2"; PUBLIC_IP=$2; shift 2 ;;
            --port) validate_arg "$1" "$2"; HTTPS_PORT=$2; shift 2 ;;
            *) stderr "Unknown argument: $1" ;;
        esac
    done
}

check_provided_args "$@"

printf "%sChecking system requirements...%s\n" "${GREEN}" "${RESET}"

if ! command -v docker >/dev/null 2>&1; then
    printf "%sDocker not installed%s\n" "${RED}" "${RESET}"
    exit 1
fi
printf "%s✓ Docker found%s\n" "${GREEN}" "${RESET}"

SERVER_VERSION=$(docker version -f "{{.Server.Version}}" 2>/dev/null | cut -d'.' -f1)
if [ "$SERVER_VERSION" -lt 17 ] 2>/dev/null; then
    printf "%sDocker version must be >= 17.05 (current: %s)%s\n" "${RED}" "$SERVER_VERSION" "${RESET}"
    exit 1
fi
printf "%s✓ Docker version OK%s\n" "${GREEN}" "${RESET}"

if [ ! -f Dockerfile ]; then
    printf "%sDockerfile not found in current directory: %s%s\n" "${RED}" "$(pwd)" "${RESET}"
    exit 1
fi
printf "%s✓ Dockerfile found%s\n" "${GREEN}" "${RESET}"

if [ ! -d src ]; then
    printf "%ssrc/ directory not found in current directory: %s%s\n" "${RED}" "$(pwd)" "${RESET}"
    exit 1
fi
printf "%s✓ src/ directory found%s\n" "${GREEN}" "${RESET}"

if [ ! -f src/bot.py ]; then
    printf "%ssrc/bot.py not found%s\n" "${RED}" "${RESET}"
    exit 1
fi
printf "%s✓ src/bot.py found%s\n" "${GREEN}" "${RESET}"

printf "%sBuilding bot image...%s\n" "${GREEN}" "${RESET}"
DOCKER_TAG=$(LC_ALL=C tr -dc a-z0-9 </dev/urandom 2>/dev/null | head -c 6 || openssl rand -hex 3 2>/dev/null || date +%s | tail -c 7)
printf "%sImage tag: skbweatherbot:%s%s\n" "${GREEN}" "$DOCKER_TAG" "${RESET}"

docker build --build-arg WEBHOOK_LISTENER="$PUBLIC_IP" \
    -t "skbweatherbot:$DOCKER_TAG" . || {
        printf "%sDocker build failed%s\n" "${RED}" "${RESET}"
        exit 1
    }

if [ -z "$(docker images "skbweatherbot:$DOCKER_TAG" -q)" ]; then
    printf "%sBuild failed - image not created%s\n" "${RED}" "${RESET}"
    exit 1
fi

printf "%s✓ Image skbweatherbot:%s built successfully%s\n" "${GREEN}" "$DOCKER_TAG" "${RESET}"

printf "%sStopping old container if exists...%s\n" "${GREEN}" "${RESET}"
docker stop skbweatherbot 2>/dev/null || true
docker rm skbweatherbot 2>/dev/null || true

printf "%sStarting container...%s\n" "${GREEN}" "${RESET}"
docker run -e OWM_KEY=$OWM_KEY -e TELEBOT_KEY=$TELEBOT_KEY \
    -e WEBHOOK_LISTENER=$PUBLIC_IP -e WEBHOOK_PORT=$HTTPS_PORT -d \
    --restart=always --name skbweatherbot \
    -p "$HTTPS_PORT:$HTTPS_PORT" \
    "skbweatherbot:$DOCKER_TAG" || {
        printf "%sFailed to start container%s\n" "${RED}" "${RESET}"
        exit 1
    }

printf "%sWaiting for container to start...%s\n" "${GREEN}" "${RESET}"
sleep 5

if docker ps | grep -q skbweatherbot; then
    printf "\n"
    printf "%s========================================%s\n" "${GREEN}" "${RESET}"
    printf "%sBot deployed successfully!%s\n" "${GREEN}" "${RESET}"
    printf "%s========================================%s\n" "${GREEN}" "${RESET}"
    printf "%sContainer: skbweatherbot%s\n" "${GREEN}" "${RESET}"
    printf "%sWebhook: https://%s:%s%s\n" "${GREEN}" "$PUBLIC_IP" "$HTTPS_PORT" "${RESET}"
    printf "%sCheck logs: docker logs -f skbweatherbot%s\n" "${GREEN}" "${RESET}"
    printf "%s========================================%s\n" "${GREEN}" "${RESET}"
else
    printf "%sDeployment failed. Container not running.%s\n" "${RED}" "${RESET}"
    printf "%sCheck logs: docker logs skbweatherbot%s\n" "${RED}" "${RESET}"
    exit 1
fi

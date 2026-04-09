set -eo pipefail

COLOR_GREEN=`tput setaf 2;`
COLOR_BLUE=`tput setaf 4;`
COLOR_NC=`tput sgr0;` # No Color

cd "$(dirname "$0")/../.."

export DJANGO_SETTINGS_MODULE="config.settings.local"
echo "${COLOR_BLUE}Starting mypy${COLOR_NC}"
uv run dmypy run -- .
echo "OK"

echo "${COLOR_BLUE}Starting Django Test with coverage${COLOR_NC}"
uv run coverage run manage.py test
uv run coverage report -m
uv run coverage html

echo "${COLOR_GREEN}Successfully Run Mypy and Test!!"

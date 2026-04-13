# 로컬 환경에서 직접 실행하는 테스트
# Docker 환경에서는 make test 쓰세뇨

set -eo pipefail

COLOR_GREEN=`tput setaf 2;`
COLOR_BLUE=`tput setaf 4;`
COLOR_NC=`tput sgr0;` # No Color

cd "$(dirname "$0")/../.."

export DJANGO_SETTINGS_MODULE="config.settings.local"

echo "${COLOR_BLUE}Starting Django Test with coverage${COLOR_NC}"
uv run coverage run manage.py test
uv run coverage report -m
uv run coverage html

echo "${COLOR_GREEN}Successfully Run Test!!"



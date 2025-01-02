

SCRIPT_DIR="/home/brookapp/python"
VENV_PATH="/home/brookapp/virtualenv/python/3.11/bin/activate"
MAIN_FILE="$SCRIPT_DIR/main.py"
LOG_FILE="$SCRIPT_DIR/logs.txt"
ERROR_LOG_FILE="$SCRIPT_DIR/errors.txt"

source "$VENV_PATH" && cd "$SCRIPT_DIR"

python "$MAIN_FILE" >> "$LOG_FILE" 2>> "$ERROR_LOG_FILE"
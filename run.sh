

SCRIPT_DIR="/home/brookapp/python"
VENV_PATH="$SCRIPT_DIR/venv/bin/activate"
MAIN_FILE="$SCRIPT_DIR/main.py"
LOG_FILE="$SCRIPT_DIR/logs.txt"
ERROR_LOG_FILE="$SCRIPT_DIR/errors.txt"

source "$VENV_PATH" && cd "$SCRIPT_DIR"

python "$MAIN_FILE" >> "$LOG_FILE" 2>> "$ERROR_LOG_FILE"
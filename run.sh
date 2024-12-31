

SCRIPT_DIR="/home/brookapp/python"
VENV_PATH="$SCRIPT_DIR/venv/bin/activate"
SCRIPT_FILE="main.py"
LOG_FILE="$SCRIPT_DIR/logs.txt"
ERROR_LOG_FILE="$SCRIPT_DIR/errors.txt"

source "$VENV_PATH" && cd "$SCRIPT_DIR"

python "$SCRIPT_DIR/$SCRIPT_FILE" >> "$LOG_FILE" 2>> "$ERROR_LOG_FILE"
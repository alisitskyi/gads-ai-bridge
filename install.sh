#!/usr/bin/env bash
# macOS / Linux Installer for gads-ai-bridge
set -e

echo "=========================================="
echo "  Installing gads-ai-bridge (Unix)        "
echo "=========================================="

PYTHON_CMD=$(which python3 || which python || true)
if [ -z "$PYTHON_CMD" ]; then
    echo "[ERROR] Python 3 is not installed or not in PATH."
    exit 1
fi
echo "[+] Found Python: $PYTHON_CMD"

echo "[*] Installing Python dependencies..."
$PYTHON_CMD -m pip install -r "$(dirname "$0")/requirements.txt" --quiet
echo "[+] Dependencies installed successfully."

GADS_HOME="$HOME/.gads"
GADS_BIN="$GADS_HOME/bin"
mkdir -p "$GADS_BIN"

cp "$(dirname "$0")/src/gads_ai/cli.py" "$GADS_HOME/gads_tool.py"

cat << 'EOF' > "$GADS_BIN/gads"
#!/usr/bin/env bash
python3 "$HOME/.gads/gads_tool.py" "$@"
EOF
chmod +x "$GADS_BIN/gads"

SHELL_RC=""
if [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
fi

if [ -n "$SHELL_RC" ]; then
    if ! grep -q "$GADS_BIN" "$SHELL_RC"; then
        echo "export PATH=\"\$PATH:$GADS_BIN\"" >> "$SHELL_RC"
        echo "[+] Added $GADS_BIN to $SHELL_RC"
    fi
fi

echo ""
echo "[+] Installation complete!"
echo "1. Run: gads config --developer-token <YOUR_TOKEN>"
echo "2. Run: gads auth"

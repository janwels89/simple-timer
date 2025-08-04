#!/bin/bash
set -e

# Always run from the script's own directory (so relative paths work!)
cd "$(dirname "$0")"

SERVICE_USER="simpletimer"
SERVICE_NAME="simple-timer"
INSTALL_DIR="/opt/simple-timer"
PYTHON_BIN="/usr/bin/python3"
VENV_DIR="$INSTALL_DIR/venv"
ENTRY="main.py"

# List of python packages provided by apt (lowercase, no version spec)
APT_PYTHON_MAP=(
    "rpi.gpio:python3-rpi.gpio"
    "gpiozero:python3-gpiozero"
    "spidev:python3-spidev"
    "smbus:python3-smbus"
    "fastapi:python3-fastapi"
    "uvicorn:python3-uvicorn"
)

usage() {
    echo "Usage: $0 [--install|--uninstall]"
    exit 1
}

if [[ "$1" == "--uninstall" ]]; then
    echo "Stopping and disabling systemd service..."
    sudo systemctl stop "$SERVICE_NAME" || true
    sudo systemctl disable "$SERVICE_NAME" || true
    echo "Removing systemd service file..."
    sudo rm -f "/etc/systemd/system/$SERVICE_NAME.service"
    sudo systemctl daemon-reload

    echo "Removing installed files..."
    sudo rm -rf "$INSTALL_DIR"

    echo "Removing user $SERVICE_USER (if exists)..."
    if id "$SERVICE_USER" &>/dev/null; then
        sudo userdel -r "$SERVICE_USER" || true
    fi

    echo "Uninstallation complete."
    exit 0
elif [[ "$1" != "--install" && "$1" != "" ]]; then
    usage
fi

echo "Installing core system dependencies..."
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip

# 1. Create dedicated user if it doesn't exist
if ! id -u "$SERVICE_USER" >/dev/null 2>&1; then
    echo "Creating user $SERVICE_USER..."
    sudo useradd -r -s /bin/false -m "$SERVICE_USER"
fi

# 2. Add user to gpio, spi, and i2c groups
echo "Adding $SERVICE_USER to gpio,spi,i2c groups..."
sudo usermod -aG gpio,spi,i2c "$SERVICE_USER"

# 3. Copy files and preserve settings.json if it exists
if [ -f "$INSTALL_DIR/settings.json" ]; then
    sudo mv "$INSTALL_DIR/settings.json" /tmp/settings.json.bak
fi

echo "Copying files to $INSTALL_DIR..."
sudo rm -rf "$INSTALL_DIR"
sudo mkdir -p "$INSTALL_DIR"

FILES=(app device features fonts static main.py requirements.txt)
# Check that all needed files/folders exist before copying
for f in "${FILES[@]}"; do
  [ -e "$f" ] || { echo "ERROR: $f not found in $(pwd)! Aborting."; exit 1; }
done

sudo cp -r "${FILES[@]}" "$INSTALL_DIR/"
sudo chown -R "$SERVICE_USER:gpio" "$INSTALL_DIR"

if [ -f /tmp/settings.json.bak ]; then
    sudo mv /tmp/settings.json.bak "$INSTALL_DIR/settings.json"
    sudo chown "$SERVICE_USER:gpio" "$INSTALL_DIR/settings.json"
fi

# 4. Install system Python packages for mapped requirements
declare -A apt_pkg_map
for mapping in "${APT_PYTHON_MAP[@]}"; do
    py_pkg="${mapping%%:*}"
    apt_pkg="${mapping##*:}"
    apt_pkg_map["$py_pkg"]="$apt_pkg"
done

APT_PKGS=()
PY_PIP_REQS=()
while IFS= read -r pkgline; do
    [[ -z "${pkgline// }" || "$pkgline" =~ ^# ]] && continue
    pkgname=$(echo "$pkgline" | awk -F'[<=>]' '{print tolower($1)}' | xargs)
    if [[ -n "${apt_pkg_map[$pkgname]}" ]]; then
        if [[ ! " ${APT_PKGS[*]} " =~ " ${apt_pkg_map[$pkgname]} " ]]; then
            APT_PKGS+=("${apt_pkg_map[$pkgname]}")
        fi
    else
        PY_PIP_REQS+=("$pkgline")
    fi
done < "$INSTALL_DIR/requirements.txt"

if [[ "${#APT_PKGS[@]}" -gt 0 ]]; then
    echo "Installing system Python packages: ${APT_PKGS[*]}"
    sudo apt-get install -y "${APT_PKGS[@]}"
fi

# 5. Create and install venv as $SERVICE_USER, only pip-install non-system requirements
echo "Creating Python venv with system site packages and installing pip dependencies..."
sudo -u "$SERVICE_USER" $PYTHON_BIN -m venv --system-site-packages "$VENV_DIR"
sudo -u "$SERVICE_USER" "$VENV_DIR/bin/pip" install --upgrade pip

if [[ "${#PY_PIP_REQS[@]}" -gt 0 ]]; then
    printf "%s\n" "${PY_PIP_REQS[@]}" > "$INSTALL_DIR/filtered_requirements.txt"
    sudo -u "$SERVICE_USER" "$VENV_DIR/bin/pip" install -r "$INSTALL_DIR/filtered_requirements.txt"
    rm "$INSTALL_DIR/filtered_requirements.txt"
else
    echo "No pip-only requirements to install."
fi

# 6. Create and enable systemd service
echo "Creating systemd service /etc/systemd/system/$SERVICE_NAME.service..."
sudo tee "/etc/systemd/system/$SERVICE_NAME.service" > /dev/null <<EOF
[Unit]
Description=Simple Timer Controller
After=multi-user.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$VENV_DIR/bin/python $ENTRY
Restart=on-failure
Environment=DISPLAY_DRIVER=real
Environment=GPIO_DRIVER=real

[Install]
WantedBy=multi-user.target
EOF

echo "Enabling and starting $SERVICE_NAME systemd service..."
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"
echo "Check status with: sudo systemctl status $SERVICE_NAME"

echo "Installation complete!"
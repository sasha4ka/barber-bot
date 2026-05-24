#!/bin/sh
set -e

CONFIG_PATH="/etc/xray/config.json"
TMP_CONFIG="/tmp/remote_config.json"

echo "=== [Initialization] Subscribing test xray ==="

if [ -z "$SUB_URL" ]; then
    echo "ERROR: enviroment SUB_URL is not provided!"
    exit 1
fi

echo "Downloading configuration"
if wget --timeout=15 -O "$TMP_CONFIG" "$SUB_URL"; then
    if [ -s "$TMP_CONFIG" ]; then
        echo "Configuration successfuly downloaded and tested"
        mv "$TMP_CONFIG" "$CONFIG_PATH"
    else
        echo "WARNING: Configuration is empty"
    fi
else
    echo "ERROR: Configuration cannot be downloaded"
fi

if [ ! -f "$CONFIG_PATH" ]; then
    echo "CRITICAL ERROR: file $CONFIG_PATH is missing"
    exit 1
fi

echo "=== [Initialization] success. Executing xray ==="
exec xray run -c "$CONFIG_PATH"
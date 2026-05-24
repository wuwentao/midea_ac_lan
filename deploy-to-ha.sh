#!/bin/bash
# Deploy modified midea_ac_lan + midea-local to Home Assistant for testing
#
# Usage: ./deploy-to-ha.sh [HA_HOST]
# Example: ./deploy-to-ha.sh homeassistant.local
#          ./deploy-to-ha.sh 192.168.1.100

set -e

HA_HOST="${1:-homeassistant.local}"
SSH_USER="root"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MIDEA_LOCAL_DIR="$SCRIPT_DIR/../midea-local"

echo "==> Deploying to $HA_HOST"

# Step 1: Deploy custom component files
echo ""
echo "--- Deploying midea_ac_lan custom component ---"
COMPONENT_PATH="/config/custom_components/midea_ac_lan"

scp "$SCRIPT_DIR/custom_components/midea_ac_lan/midea_devices.py" \
    "$SSH_USER@$HA_HOST:$COMPONENT_PATH/midea_devices.py"

scp "$SCRIPT_DIR/custom_components/midea_ac_lan/translations/en.json" \
    "$SSH_USER@$HA_HOST:$COMPONENT_PATH/translations/en.json"

scp "$SCRIPT_DIR/custom_components/midea_ac_lan/translations/zh-Hans.json" \
    "$SSH_USER@$HA_HOST:$COMPONENT_PATH/translations/zh-Hans.json"

echo "Custom component files deployed."

# Step 2: Find and deploy midea-local library
echo ""
echo "--- Deploying midea-local library ---"

# Find the midea-local installation path
MIDEA_LIB_PATH=$(ssh "$SSH_USER@$HA_HOST" \
    "find / -path '*/midealocal/devices/ac/__init__.py' 2>/dev/null | head -1 | xargs dirname")

if [ -z "$MIDEA_LIB_PATH" ]; then
    echo "ERROR: Could not find midealocal installation on $HA_HOST"
    echo "You may need to find it manually:"
    echo "  ssh $SSH_USER@$HA_HOST 'find / -name midealocal -type d 2>/dev/null'"
    exit 1
fi

echo "Found midea-local at: $MIDEA_LIB_PATH"

scp "$MIDEA_LOCAL_DIR/midealocal/devices/ac/__init__.py" \
    "$SSH_USER@$HA_HOST:$MIDEA_LIB_PATH/__init__.py"

scp "$MIDEA_LOCAL_DIR/midealocal/devices/ac/message.py" \
    "$SSH_USER@$HA_HOST:$MIDEA_LIB_PATH/message.py"

echo "midea-local library deployed."

# Step 3: Restart HA
echo ""
echo "--- Restarting Home Assistant ---"
ssh "$SSH_USER@$HA_HOST" "ha core restart" 2>/dev/null || \
    echo "NOTE: Could not auto-restart. Please restart HA manually via Settings → System → Restart"

echo ""
echo "==> Done! After HA restarts:"
echo "    1. Go to Settings → Devices & Services → Midea AC LAN"
echo "    2. Click CONFIGURE on your PortaSplit device"
echo "    3. Enable 'Outdoor Silent Mode' in extra switches"
echo "    4. The new switch should appear for your device"

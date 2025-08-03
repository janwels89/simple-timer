#!/bin/bash
set -e

TARGET_USER="dietpi"
TARGET_HOST="192.168.1.167"
TARGET_PASS="password"
TAR_FILE="timer.tar.gz"
REMOTE_DIR="/tmp"
INSTALLER="install.sh"

# 1. Copy build artifact to remote host using sshpass
echo "Copying build_simple-timer* to $TARGET_USER@$TARGET_HOST:$REMOTE_DIR/$TAR_FILE ..."
cat build_simple-timer* | sshpass -p "$TARGET_PASS" ssh -o StrictHostKeyChecking=no ${TARGET_USER}@${TARGET_HOST} "cat > ${REMOTE_DIR}/${TAR_FILE}"

# 2. SSH to remote host, extract, run installer from subdirectory
echo "Connecting to remote host to extract and install..."
sshpass -p "$TARGET_PASS" ssh -o StrictHostKeyChecking=no ${TARGET_USER}@${TARGET_HOST} "
    set -e
    cd ${REMOTE_DIR}
    tar xzf ${TAR_FILE}
    # Find the first directory that was extracted
    EXTRACTED_DIR=\$(tar tf ${TAR_FILE} | head -1 | cut -d/ -f1)
    if [ -d \"\$EXTRACTED_DIR\" ]; then
        cd \"\$EXTRACTED_DIR\"
        if [ -f ${INSTALLER} ]; then
            sudo bash ${INSTALLER} --install
        else
            echo \"Installer (${INSTALLER}) not found after extraction!\"
            exit 1
        fi
    else
        echo \"Extracted directory (\$EXTRACTED_DIR) not found!\"
        exit 1
    fi
"

echo "Deployment and installation finished!"
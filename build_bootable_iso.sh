#!/usr/bin/env bash
# Vision OS Bootable Image Builder (Safe Dual-Boot / USB Live Environment)
# Packages a minimal Linux kernel + Xorg + Python3 + Vision OS Shell (~180 MB ISO)

set -e
echo "=== Building Vision OS Bootable Minimal Environment ==="
mkdir -p build/rootfs/opt/vision-os
cp vision_os.py vision_sdk.py profiles.json build/rootfs/opt/vision-os/

cat << 'EOF' > build/rootfs/opt/vision-os/start_vision.sh
#!/bin/sh
xsetroot -solid "#060b14"
exec python3 /opt/vision-os/vision_os.py
EOF
chmod +x build/rootfs/opt/vision-os/start_vision.sh

echo "[OK] Rootfs staged at build/rootfs/opt/vision-os"
echo "[Next] Package with live-build / xorriso or add a GRUB loopback entry on a separate FAT32/EXT4 partition without touching Windows NTFS."
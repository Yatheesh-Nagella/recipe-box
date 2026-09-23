#!/usr/bin/env bash
# One-time setup on the Pi: installs the systemd timer that runs deploy.sh.
# Usage (from your normal user): sudo ./deploy/install.sh
set -euo pipefail

if [ "$(id -u)" -ne 0 ] || [ -z "${SUDO_USER:-}" ]; then
  echo "run this via sudo from your normal user: sudo ./deploy/install.sh" >&2
  exit 1
fi

deploy_home=$(getent passwd "$SUDO_USER" | cut -d: -f6)
repo_dir="${REPO_DIR:-$deploy_home/recipe-box}"

sed -e "s|__USER__|$SUDO_USER|g" -e "s|__REPO_DIR__|$repo_dir|g" \
  "$repo_dir/deploy/recipe-box-deploy.service" >/etc/systemd/system/recipe-box-deploy.service
install -m 644 "$repo_dir/deploy/recipe-box-deploy.timer" /etc/systemd/system/recipe-box-deploy.timer

systemctl daemon-reload
systemctl enable --now recipe-box-deploy.timer
echo "installed. next run: systemctl list-timers recipe-box-deploy.timer"
echo "logs:               journalctl -u recipe-box-deploy -n 50"

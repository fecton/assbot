#!/bin/bash

echo "[INFO] Moved assbot.service to /etc/systemd/system/" && \
systemctl daemon-reload && \
systemctl enable assbot && \
systemctl start assbot && \
systemctl status assbot


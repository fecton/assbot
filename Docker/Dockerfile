# OS
FROM debian
RUN
	./docker-run.sh
COPY assbot.service /etc/systemd/system/
RUN
	echo "[INFO] Moved assbot.service to /etc/systemd/system/" && \
	systemctl daemon-reload && \
	systemctl enable assbot && \
	systemctl start assbot && \
	systemctl status assbot

ENTRYPOINT ["/usr/games/assbot"]




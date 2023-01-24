FROM ubuntu:latest


RUN echo "[INFO] Installing python and pip"
RUN apt update -y
RUN apt install -y \
	python3 \
	python3-pip \
	git
RUN python3 --version && \
	pip3 --version


RUN echo "[INFO] Clonning the repository and install python requirements"
RUN	cd /usr/games/ && \
	git clone https://github.com/fecton/assbot.git -b container && \
	cd assbot && \
	chmod +x app.py && \
	pip3 install -r requirements.txt 

COPY .env /usr/games/assbot

ENV ASSBOT_DOCKER=1

CMD ["python3", "/usr/games/assbot/app.py", "-DFOREGROUND"]

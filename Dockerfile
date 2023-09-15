FROM ubuntu:23.10

# Install dependencies
RUN apt update -y
RUN apt install -y \
	python3 \
	python3-pip \
	git

# Check versions
RUN python3 --version && \
	pip3 --version

# Prepare assbot sources
RUN	cd /usr/games/ && \
	git clone https://github.com/fecton/assbot.git -b container && \
	cd assbot && \
	chmod +x app.py

RUN pip3 install -r requirements.txt 

# TODO: creds should be transfer safefully
COPY ../.env /usr/games/assbot

WORKDIR /usr/games/assbot

CMD ["python3", "/usr/games/assbot/app.py", "-DFOREGROUND"]

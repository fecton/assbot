# OS
FROM test/pyserver

# Copying a service file to the docker
COPY assbot.service /etc/systemd/system/

# Bulding the container
RUN	cd /usr/games/ && \
	git clone https://github.com/fecton/assbot.git && \
	cd assbot && \
	chmod +x app.py && \
	pip3 install -r requirements.txt && \
	echo "TOKEN=" >  .env && \
	echo "OWNER=" >> .env 

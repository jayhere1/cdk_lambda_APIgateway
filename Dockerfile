FROM ubuntu:latest

ENV DOCKER_UID $DOCKER_UID

RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y \
        curl \
        gnupg \
        python3-pip \
        python3 \
    &&apt-get clean

RUN ln -s usr/bin/python3 usr/bin/python
RUN curl -sL https://deb.nodesource.com/setup_16.x | bash -\
    && apt-get install -y nodejs
RUN pip3 install --upgrade pip
RUN npm install -g aws-cdk

RUN mkdir -p /app
WORKDIR /app
COPY ./ /app
RUN pip3 install -r requirements.txt
CMD["/bin/bash", "-c"]
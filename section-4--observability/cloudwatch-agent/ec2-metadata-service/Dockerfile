# json-server is a simple tool to serve a JSON file through a REST API
# we will use it to serve the ec2-metadata.json file to mock the EC2 metadata service

FROM node:latest

RUN npm install -g json-server

COPY ./ec2-metadata.json /root/ec2-metadata.json

ENTRYPOINT ["json-server", "/root/ec2-metadata.json"]
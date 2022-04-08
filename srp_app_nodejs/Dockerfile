FROM node:12.18.1
WORKDIR /
COPY ["package.json", "package-lock.json*", "./"]
RUN npm install
CMD [ "node", "server.js" ]

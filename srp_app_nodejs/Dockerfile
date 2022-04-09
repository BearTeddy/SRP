FROM node:12.18.1
WORKDIR /
COPY ./srp_app_nodejs .
RUN cd ./srp_app_nodejs
RUN npm install
CMD [ "node", "server.js" ]

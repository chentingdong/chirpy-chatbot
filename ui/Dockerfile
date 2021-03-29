FROM node:11.12.0

RUN apt update && \
  apt install -y vim

#Cache npm install layer and pointing npm to a registry to speed up
WORKDIR /app/ui
RUN npm install -g @vue/cli node-notifier
COPY package.json /app/ui/package.json
COPY package-lock.json /app/ui/package-lock.json
RUN npm config set loglevel warn && npm install
RUN npm rebuild node-sass

ADD . /app/ui

# ENV
ENV PATH="/app/ui/node_modules/webpack-dev-server/bin/:${PATH}"
EXPOSE 2000

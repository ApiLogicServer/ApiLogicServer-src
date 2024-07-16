# To build image for your ApiLogicProject, see build_image.sh
#    $ sh devops/docker-image-ont/build_image.sh .

# consider adding your version here

# ensure platform for common amd deployment, even if running on M1/2 mac --platform=linux/amd64
FROM node:18

USER root
RUN apt-get update \
    && apt-get install nano \
    && export TERM=xterm

#USER node
WORKDIR /home/node

COPY ../../ui/yaml .
COPY ./*.ts /home/node/src/environments/.

#USER root
# enables docker to write into container, for sqlite
RUN chown -R node /home/node
RUN npm install
CMD ["tail", "-f", "/dev/null" ]
#CMD [ "npm", "start" ]
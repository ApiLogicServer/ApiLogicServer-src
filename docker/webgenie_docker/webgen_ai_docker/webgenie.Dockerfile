
# see docker/webgenie_docker/build_web_genie.sh

FROM apilogicserver/api_logic_server 

USER root

RUN apt-get update
RUN apt-get install -y nginx
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
RUN npm install -g @softwaretechnik/dbml-renderer
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/wg.conf /etc/nginx/wg.conf
RUN mkdir /etc/nginx/apis
RUN chown -R api_logic_server /var/log/nginx /etc/nginx/apis
RUN chown api_logic_server /var/lib/nginx
RUN chmod 777 /run # TODO!! security issue?

RUN mkdir -p /opt/projects
COPY webgenai/webgenai /opt/webgenai
RUN rm -fr /home/api_logic_server/api_logic_server_cli/create_from_model/safrs-react-admin-npm-build
COPY sra/build /home/api_logic_server/api_logic_server_cli/create_from_model/safrs-react-admin-npm-build
RUN chown -R api_logic_server /opt /home/api_logic_server
USER api_logic_server

EXPOSE 5656-7000

CMD ["bash", "-c", "/opt/webgenai/arun.sh"]

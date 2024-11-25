
# see docker/webgenie_docker/build_web_genie.sh

FROM apilogicserver/api_logic_server_local

USER root

RUN apt-get update
RUN apt-get install -y nginx jq sqlite3
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install wget -y \
    && mkdir -p -m 755 /etc/apt/keyrings \
    && wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg | tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
    && chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt update \
    && apt install gh -y

RUN npm install -g @softwaretechnik/dbml-renderer
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/wg.conf /etc/nginx/wg.conf
RUN mkdir -p /etc/nginx/apis
RUN chown -R api_logic_server /var/log/nginx /etc/nginx/apis
RUN chown api_logic_server /var/lib/nginx
RUN chmod 777 /run # TODO!! security issue?

RUN mkdir -p /opt/projects
COPY webgenai/webgenai /opt/webgenai
RUN cd /opt/webgenai/simple-spa && npm install
RUN rm -fr /home/api_logic_server/api_logic_server_cli/create_from_model/safrs-react-admin-npm-build
COPY sra/build /home/api_logic_server/api_logic_server_cli/create_from_model/safrs-react-admin-npm-build
RUN chown -R api_logic_server /opt /home/api_logic_server
USER api_logic_server

EXPOSE 5656-7000

CMD ["bash", "-c", "/opt/webgenai/arun.sh"]

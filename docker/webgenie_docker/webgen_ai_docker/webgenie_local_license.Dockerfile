# see docker/webgenie_docker/build_web_genie.sh

FROM apilogicserver/api_logic_server_local

USER root

RUN apt-get clean
RUN echo 'Acquire::http::Pipeline-Depth 0;\nAcquire::http::No-Cache true;\nAcquire::BrokenProxy true;\n' > /etc/apt/apt.conf.d/99fixbadproxy

RUN apt-get update
RUN apt-get install -y nginx jq sqlite3
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN npm install -g @softwaretechnik/dbml-renderer
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/wg.conf /etc/nginx/wg.conf
COPY license/license_checker.py /home/license/license_checker.py
COPY license/startup.sh /home/license/startup.sh
RUN chmod +x /home/license/startup.sh
RUN mkdir -p /etc/nginx/apis
RUN chown -R api_logic_server /var/log/nginx /etc/nginx/apis
RUN chown api_logic_server /var/lib/nginx
RUN chmod 777 /run # TODO!! security issue?

RUN mkdir -p /opt/projects
COPY webgenai/webgenai /opt/webgenai
# COPY arun.sh /opt/webgenai/arun.sh
RUN cd /opt/webgenai/simple-spa && npm install
RUN rm -fr /home/api_logic_server/api_logic_server_cli/create_from_model/safrs-react-admin-npm-build
COPY sra/build /home/api_logic_server/api_logic_server_cli/create_from_model/safrs-react-admin-npm-build
RUN chown -R api_logic_server /etc/nginx /opt /home/api_logic_server
USER api_logic_server
RUN pip install colorama astor

EXPOSE 5656-7000

# CMD ["bash", "-c", "/opt/webgenai/arun.sh"]
CMD ["bash", "-c", "/home/license/startup.sh"]
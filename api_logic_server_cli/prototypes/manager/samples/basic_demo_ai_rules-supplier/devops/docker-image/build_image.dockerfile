# To build image for your ApiLogicProject, see build_image.sh
#    $ sh devops/docker-image/build_image.sh .

# consider adding your version here

# ensure platform for common amd deployment, even if running on M1/2 mac --platform=linux/amd64
FROM --platform=linux/amd64 apilogicserver/api_logic_server
# FROM apilogicserver/api_logic_server  

USER root

# this project's AI Rules (logic/logic_discovery ai_requests/*) call openai directly at runtime;
# the base image no longer bundles it (moved to an optional extra to keep the base image openai-free)
RUN pip install openai==1.55.3

# user api_logic_server comes from apilogicserver/api_logic_server
WORKDIR /home/api_logic_project
# USER api_logic_server
COPY ../../ .

# enables docker to write into container, for sqlite
RUN chown -R api_logic_server /home/api_logic_project

CMD [ "python", "./api_logic_server_run.py" ]
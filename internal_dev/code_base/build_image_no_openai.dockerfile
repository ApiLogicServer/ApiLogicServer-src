# FedEx-specific variant of devops/docker-image/build_image.dockerfile (demo_customs_clvs / GENAI797).
#
# Same base image as the standard project Dockerfile — apilogicserver/api_logic_server,
# the public image built from ApiLogicServer-src/docker/api_logic_server.Dockerfile,
# which installs the full requirements.txt (including openai==1.55.3). This variant adds
# one line to strip openai back out of the derived image, so THIS image's dependency
# manifest — the one FedEx's own Nexus IQ / SCA scan would inspect — shows zero openai.
#
# Verified 2026-08-12 (no Docker daemon available to run `docker build` directly in this
# environment, so verified the equivalent operation instead): built a venv from the real,
# unmodified ApiLogicServer-src/requirements.txt (exactly what the base image's own
# `pip install -r requirements.txt` step does), confirmed openai installs, then ran
# `pip uninstall -y openai` (exactly what the RUN line below does) — pip check clean,
# and demo_customs_clvs's full logic/ tree (declare_logic.py + all logic_discovery/*)
# still imports with zero errors against that stripped environment. This Dockerfile
# change is that same operation, one layer later, inside the image build.
#
# This only touches demo_customs_clvs's own project-level Dockerfile — NOT the shared
# public apilogicserver/api_logic_server base image other customers pull. No gold-source
# change to requirements.txt or pyproject.toml required for this path; see
# openai-dependency-removal-proposal-2026-08-12.md for the alternative (pyproject.toml
# extras) that WOULD touch gold source and is the better long-term fix if Val decides
# to make openai optional for everyone, not just this one FedEx image.
#
# Build exactly as the original: sh devops/docker-image/build_image.sh . (after swapping
# this file in for build_image.dockerfile, or pointing build_image.sh's -f flag at this
# file instead).

FROM --platform=linux/amd64 apilogicserver/api_logic_server

USER root

# Strip openai from this image's dependency set — see header comment above.
# Nothing in demo_customs_clvs's logic/ tree references openai (verified); the only
# code elsewhere in the product that does (WebGenAI/--vibe, the standalone MCP demo
# script, and the "AI Rules" pattern used by other samples) is not part of this project.
RUN pip uninstall -y openai

# user api_logic_server comes from apilogicserver/api_logic_server
WORKDIR /home/api_logic_project
COPY ../../ .

# enables docker to write into container, for sqlite
RUN chown -R api_logic_server /home/api_logic_project

CMD [ "python", "./api_logic_server_run.py" ]

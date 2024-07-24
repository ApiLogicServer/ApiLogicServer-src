# Stage 1: Compile and Build angular codebase
# Use official node image as the base image
# cd ui/yaml
# docker build -f Dockerfile -t tylerm007/yaml_editor --rm .
# docker tag tylerm007/yaml_editor tylerm007/yaml_editor:1.0.11
# docker push tylerm007/yaml_editor:1.0.11  # requires docker login
#
# docker tag tylerm007/yaml_editor tylerm007/yaml_editor:latest
# docker push tylerm007/yaml_editor:latest  
#
#  curl -X POST http://apilogicserver:5655/ontimizeweb/services/rest/users/login -H 'Authorization: Basic YWRtaW46cA=='
FROM node:18.10.0-alpine as build
USER root

# Set the working directory
WORKDIR /usr/local/app

COPY package*.json .

# Install all the dependencies
RUN npm install

COPY . .

# Generate the build of the application
RUN npm run production


# Stage 2: Serve app with nginx server

# Use official nginx image as the base image
FROM nginx:latest

# Copy the build output to replace the default nginx contents.
COPY --from=build /usr/local/app/dist /usr/share/nginx/html
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

#RUN chown root /usr/share/nginx/html/*

#and changed permissions using:

#RUN chmod 755 /usr/share/nginx/html/*
# Expose port 80
EXPOSE 80

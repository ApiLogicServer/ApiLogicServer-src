# Stage 1: Compile and Build angular codebase
# Use official node image as the base image
# docker build -f Dockerfile -t apilogicserver/ontimizeweb --rm .
FROM node:18.10.0-alpine as build

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

# Expose port 80
EXPOSE 80

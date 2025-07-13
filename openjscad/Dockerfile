# Use the official Node.js image
FROM node:24

# Install OpenJSCAD CLI at version 1.10.0 -- 1.10.2 is the version of the web ui which worked
RUN npm install -g @jscad/cli@1.10.0

COPY convert-all.sh /usr/local/bin/convert-all.sh

RUN chmod +x /usr/local/bin/convert-all.sh

# Set working directory
WORKDIR /designs


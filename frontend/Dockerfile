# Use an official Node.js runtime as a parent image
FROM node:16

# Set the working directory in the container
WORKDIR /app

# Copy the package.json and package-lock.json first for faster builds
COPY package*.json /app/

# Install the dependencies
RUN npm install

# Copy the rest of the application files
COPY . /app/

# Expose port 3000 to access the React app
EXPOSE 3000

# Run the React app
CMD ["npm", "start"]

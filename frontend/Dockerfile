FROM node:16

# working directory
WORKDIR /app

# Copy the package.json and package-lock.json first for faster builds
COPY package*.json /app/


RUN npm install

# Copy the rest of the files
COPY . /app/

# React app port
EXPOSE 3000

# Run the React app
CMD ["npm", "start"]

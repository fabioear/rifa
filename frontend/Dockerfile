FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

# Expose internal port
EXPOSE 5173

# Run in development mode (or preview if built)
# Using dev mode with --host to allow external access
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]

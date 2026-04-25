FROM node:20-alpine

WORKDIR /app

# Copy package configurations
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application source
COPY . .

# Expose Vite default port
EXPOSE 5173

# Command is handled in docker-compose.yml for development
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

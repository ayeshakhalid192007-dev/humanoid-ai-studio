FROM node:20-slim

WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

# Copy source code
COPY src/ ./src/

# Expose port (Railway sets PORT env var)
EXPOSE 3002

# Start with crypto polyfill preloaded
CMD ["node", "--require", "./src/crypto-polyfill.cjs", "src/index.js"]

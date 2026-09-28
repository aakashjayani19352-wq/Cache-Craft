# Cache-Craft Next.js Frontend Dockerfile
FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm ci --legacy-peer-deps || npm install --legacy-peer-deps

# Copy source
COPY . .

# Expose Next.js port
EXPOSE 3000

ENV PORT=3000
ENV NODE_ENV=development
ENV NEXT_PUBLIC_API_URL=http://backend:8000

CMD ["npm", "run", "dev"]

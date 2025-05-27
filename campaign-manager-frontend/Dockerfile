# Frontend Dockerfile
FROM node:18

WORKDIR /app

# Set NODE_ENV to development
ENV NODE_ENV=development

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies with the exact versions needed
RUN npm install
RUN npm install -g vite@4.5.14
RUN npm install -g tailwindcss@3.3.3 postcss@8.4.24 autoprefixer@10.4.14

# Create directories for Tailwind CSS
RUN mkdir -p /app/src

# Copy configuration files first
COPY postcss.config.js tailwind.config.js vite.config.js ./

# Copy source code
COPY . .

# Explicitly verify that Tailwind CSS is installed and available
RUN npx tailwindcss --help || echo "Tailwind CSS is not available"

# Expose Vite dev server port
EXPOSE 5173

# Start dev server with host flag and debug output
CMD ["npm", "run", "dev", "--", "--host"]

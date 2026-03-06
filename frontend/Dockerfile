# Development stage: source mounted at runtime, deps installed via scripts/npm.sh
FROM node:20-alpine AS dev
WORKDIR /app
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Build stage: install deps + build
FROM node:20-alpine AS build
ARG APP_VERSION=dev
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN echo "$APP_VERSION" > ../VERSION && npm run build

# Production stage: serve built assets with nginx
FROM nginx:alpine AS prod

LABEL org.opencontainers.image.source="https://github.com/VEAF/website-2026"
LABEL org.opencontainers.image.description="VEAF Website 2026 - Frontend"

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]

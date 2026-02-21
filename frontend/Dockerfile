# Development stage: source mounted at runtime, deps installed via scripts/npm.sh
FROM node:20-alpine AS dev
WORKDIR /app
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Build stage: deps + source + build
FROM dev AS build
COPY . .
RUN npm run build

# Production stage: serve built assets
FROM nginx:alpine AS prod
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

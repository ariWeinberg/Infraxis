FROM node:22-alpine AS build
WORKDIR /app
COPY apps/console/package.json apps/console/package-lock.json* ./
RUN npm install
COPY apps/console ./
RUN npm run build
FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
USER 101

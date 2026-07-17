FROM node:24-alpine AS frontend

ARG VITE_SOURCEMAP=false
ARG VITE_API_HOST=
ARG VITE_IMAGES_HOST=/static/i

WORKDIR /opt

COPY ./frontend ./

RUN npm ci

RUN npx tsc -b && npx vite build --outDir="./dist" --emptyOutDir --sourcemap=false

FROM nginx:stable-alpine AS nginx

RUN mkdir -p /usr/share/nginx/html/static

COPY --from=frontend /opt/dist /usr/share/nginx/html/static

COPY ./static/i/ /usr/share/nginx/html/static/i/
COPY ./nginx/config/nginx.conf /etc/nginx/nginx.conf
COPY ./nginx/ssl /etc/nginx/ssl

EXPOSE 80
EXPOSE 443

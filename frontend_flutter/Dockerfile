FROM ghcr.io/cirruslabs/flutter:3.27.0-0.1.pre AS build-env

WORKDIR /app

COPY . /app/

RUN flutter build web --release --web-renderer html



FROM nginx:alpine

COPY --from=build-env /app/build/web /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
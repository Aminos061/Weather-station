FROM debian:latest AS build-env

# Install necessary dependencies for running Flutter on web
RUN apt-get update && apt-get install -y \
    libxi6 libgtk-3-0 libxrender1 libxtst6 libxslt1.1 curl git wget unzip libgconf-2-4 gdb \
    libstdc++6 libglu1-mesa fonts-droid-fallback lib32stdc++6 python3 && apt-get clean

# Clone the Flutter repository
RUN git clone https://github.com/flutter/flutter.git /usr/local/flutter

# Set Flutter path
ENV PATH="/usr/local/flutter/bin:/usr/local/flutter/bin/cache/dart-sdk/bin:${PATH}"

# Flutter setup commands
RUN flutter doctor -v
RUN flutter channel master
RUN flutter upgrade

# Enable web support for Flutter
RUN flutter config --enable-web

# Create and set the working directory
RUN mkdir /app/
COPY . /app/
WORKDIR /app/

# Build the Flutter web application with the HTML renderer
RUN flutter build web --release --web-renderer html

# Use Nginx to serve the web app
FROM nginx:1.21.1-alpine

# Copy the Flutter build to the Nginx HTML folder
COPY --from=build-env /app/build/web /usr/share/nginx/html

# Expose port 80 (Nginx default port)
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]

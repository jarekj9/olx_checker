FROM python:3-slim

ARG USER=jarek
ARG USERID=1000

# add user to chown/share volumes
RUN groupadd -g $USERID -o $USER
RUN useradd -m -u $USERID -g $USERID -o -s /bin/bash $USER

# install nginx
RUN apt-get update && apt-get upgrade -y && apt-get autoremove && apt-get autoclean
RUN apt-get update && apt-get install nginx -y --no-install-recommends
RUN apt-get install -y \
    libffi-dev \
    libssl-dev \
    default-libmysqlclient-dev \
    libxml2-dev \
    libxslt-dev \
    libjpeg-dev \
    libfreetype6-dev \
    zlib1g-dev \
    vim

COPY nginx/nginx.default /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

# copy source and install dependencies
RUN mkdir -p /opt/app/flask-react/app
COPY requirements.txt start-server.sh /opt/app/
COPY app /opt/app/flask-react/app
WORKDIR /opt/app
RUN pip install --upgrade pip
RUN mkdir -p /opt/app/pip_cache
RUN pip install -r requirements.txt --cache-dir /opt/app/pip_cache
RUN chown -R www-data:www-data /opt/app

WORKDIR /opt/app/flask-react/app

# Server
STOPSIGNAL SIGINT
ENTRYPOINT ["sh"]
CMD ["/opt/app/start-server.sh"]

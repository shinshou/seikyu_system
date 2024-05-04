FROM python:3.10
ENV PYTHONUNBUFFERED 1
RUN mkdir -p /var/www/inventory
WORKDIR /var/www/inventory
ADD requirements.txt /var/www/inventory/
RUN pip3 install -r requirements.txt
RUN apt update
RUN apt install gettext -y
ADD . /var/www/inventory/
EXPOSE 8000
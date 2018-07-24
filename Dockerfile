FROM python:2.7
LABEL maintainer="Hossam Hammady <github@hammady.net>"

RUN apt-get update && \
    apt-get install -y inkscape

COPY . /home

CMD ["/home/svg2png.sh", "800", "10", "/home/samples/svg", "/home/output/images"]

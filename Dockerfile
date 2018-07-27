FROM python:2.7
LABEL maintainer="Hossam Hammady <github@hammady.net>"

RUN apt-get update && \
    apt-get install -y inkscape && \
    pip install --upgrade pip

WORKDIR /home

COPY requirements.txt /home/
RUN pip install -r requirements.txt

COPY . /home

CMD ["/bin/bash"]

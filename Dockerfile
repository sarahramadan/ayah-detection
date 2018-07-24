FROM python:2.7
LABEL maintainer="Hossam Hammady <github@hammady.net>"

RUN apt-get update && \
    apt-get install -y inkscape && \
    pip install --upgrade pip

WORKDIR /home

COPY requirements.txt /home/
RUN pip install -r requirements.txt

COPY . /home

#CMD ["python"]
CMD ["./svg2png.sh", "800", "10", "./samples/svg", "./output/images"]
# CMD ["python", "./fix_color_mode.py", "./output/images/800"]

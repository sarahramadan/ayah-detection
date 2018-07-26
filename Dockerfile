FROM python:2.7
LABEL maintainer="Hossam Hammady <github@hammady.net>"

RUN apt-get update && \
    apt-get install -y inkscape && \
    pip install --upgrade pip

WORKDIR /home

COPY requirements.txt /home/
RUN pip install -r requirements.txt

COPY . /home

# CMD ["./svg2png.sh", "800", "10", "/svg", "./output/images"]
# CMD ["python", "./fix_color_mode.py", "./output/images/800"]
CMD ["python", "./main.py", "./output/images/800", "./separator1.png", "./separator2.png", "./output", "1"]

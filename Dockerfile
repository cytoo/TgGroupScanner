FROM alphine

RUN apk --update --no-cahce add \
    python3 python3-dev

WORKDIR /app
ADD . /app
RUN pip3 install -U pip
RUN pip3 install -r --upgrade requirements.txt

CMD ["python3","main.py"]
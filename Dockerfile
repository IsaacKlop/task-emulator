FROM python:rc-slim

RUN apt-get update \
    && apt-get install -y iperf3 \
    && apt-get install -y stress

#Expose default iperf server port:
EXPOSE 5201

WORKDIR /app

ADD . /app

ENTRYPOINT ["python", "emulate-task.py"]

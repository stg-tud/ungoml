FROM golang:1.20.0-bullseye

ENV CONTAINER_MODE true

RUN apt-get update && \
  apt-get install -y -o APT::Install-Recommends=false -o APT::Install-Suggests=false \
  docker.io \
  git \
  python3 \
  wget \
  ca-certificates \
  python3-pip \
  sudo \
  ssh \
  && apt-get clean
#RUN apt-get clean

# Install go-geiger
RUN go install github.com/jlauinger/go-geiger@latest

COPY requirements.txt /unsafe-toolkit/

WORKDIR  /unsafe-toolkit

RUN pip install -r requirements.txt

RUN git config --global core.sshCommand 'ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'

COPY . /unsafe-toolkit

ENTRYPOINT [ "python3" ]
CMD ["evaluate.py"]
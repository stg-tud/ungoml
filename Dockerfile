FROM debian:bullseye

ENV GOPATH /root/go
ENV PATH $PATH:/usr/local/go/bin:$GOPATH/bin
ENV GO_VERSION 1.17.7
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
  ssh

RUN apt-get clean

RUN wget https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz && tar xvf go${GO_VERSION}.linux-amd64.tar.gz && sudo mv go /usr/local

# Install go-geiger
RUN go get github.com/jlauinger/go-geiger

COPY requirements.txt /unsafe-toolkit/

WORKDIR  /unsafe-toolkit

RUN pip install -r requirements.txt

RUN git config --global core.sshCommand 'ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'

COPY . /unsafe-toolkit

ENTRYPOINT [ "python3", "evaluate.py" ]
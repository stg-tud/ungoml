FROM debian:bullseye

ENV GOPATH /go/
ENV PATH $PATH:/go/bin/

RUN apt-get update && \
  apt-get install -y -o APT::Install-Recommends=false -o APT::Install-Suggests=false \
  docker.io \
  git \
  python3 \
  wget \
  ca-certificates \
  golang \ 
  python3-pip 

# Install go-geiger
RUN go get github.com/jlauinger/go-geiger

COPY . /unsafe-toolkit
WORKDIR  /unsafe-toolkit

RUN pip install -r requirements.txt

ENTRYPOINT [ "python3", "run.py" ]
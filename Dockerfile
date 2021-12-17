FROM debian

ENV GOROOT /usr/lib/go
ENV GOPATH /go
ENV PATH /go/bin:$PATH

ARG GOLANG_VERSION 1.14.3


RUN apt-get update && \
  apt-get install -y -o APT::Install-Recommends=false -o APT::Install-Suggests=false \
  docker.io \
  git 

# Install Go: https://stackoverflow.com/questions/52056387/how-to-install-go-in-alpine-linux
RUN wget https://dl.google.com/go/go$GOLANG_VERSION.src.tar.gz && tar -C /usr/local -xzf go$GOLANG_VERSION.src.tar.gz
RUN cd /usr/local/go/src && ./make.bash
ENV PATH=$PATH:/usr/local/go/bin
RUN rm go$GOLANG_VERSION.src.tar.gz


CMD [ "" ]

ENTRYPOINT [ "/bin/bash" ]
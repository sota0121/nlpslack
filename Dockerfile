FROM ubuntu:18.04
 
ENV PYTHON_VERSION 3.7.3
ENV HOME /root
# PYTHON
ENV PYTHON_ROOT $HOME/local/bin/python-$PYTHON_VERSION
ENV PATH $PYTHON_ROOT/bin:$PATH
ENV PYENV_ROOT $HOME/.pyenv
 
RUN apt-get update && apt-get upgrade -y \
 && apt-get install -y tzdata

# timezone setting
ENV TZ=Asia/Tokyo
RUN apt-get install -y tzdata \
    build-essential \
    curl \
    git \
    libbz2-dev \
    libcurl4-openssl-dev \
    libffi-dev \
    liblzma-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libpq-dev \
    libreadline-dev \
    libsqlite3-dev \
    libssl-dev \
    libxml2-dev \
    llvm \
    make \
    r-base \
    tk-dev \
    unzip \
    vim \
    wget \
    xz-utils \
    zlib1g-dev \
 && apt-get autoremove -y && apt-get clean \
 && git clone https://github.com/pyenv/pyenv.git $PYENV_ROOT \
 && $PYENV_ROOT/plugins/python-build/install.sh \
 && /usr/local/bin/python-build -v $PYTHON_VERSION $PYTHON_ROOT \
 && rm -rf $PYENV_ROOT

 # install additional packages
COPY ./requirements.txt requirements.txt
RUN pip install -U pip && pip install -r requirements.txt
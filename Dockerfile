ARG ATOM_IMAGE=elementaryrobotics/atom:v1.5.0-opencv-amd64

FROM ${ATOM_IMAGE}

RUN apt-get update && apt-get install -y \
  --no-install-recommends \
  libglvnd0 \
  libgl1 \
  libglx0 \
  libegl1 \
  libgles2 \
  tzdata \
  libxkbcommon-x11-0 \
  libglib2.0-0 \
  qt5-default

#
# Install python dependencies
#

ADD ./requirements.txt /code/requirements.txt

# Upgrade pip for latest PyQt5
RUN pip3 install --upgrade pip \
    && pip3 install --no-cache-dir -r /code/requirements.txt

ADD . /code
WORKDIR /code


# Finally, specify the command we should run when the app is launched
RUN chmod +x launch.sh
CMD ["/bin/bash", "launch.sh"]

ARG ATOM_IMAGE=elementaryrobotics/atom:v1.5.0-opencv-amd64

FROM ${ATOM_IMAGE}

# Install the requirements
ADD ./requirements.txt /code/requirements.txt
# Upgrade pip for latest PyQt5
RUN pip3 install --upgrade pip && pip3 install wheel \
    && pip3 install --no-cache-dir -r /code/requirements.txt

ADD . /code
WORKDIR /code

# Finally, specify the command we should run when the app is launched
CMD ["/bin/bash", "launch.sh"]

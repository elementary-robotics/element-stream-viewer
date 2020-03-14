FROM elementaryrobotics/atom-opengl:v1.2.2

# libxkbcommon-x11 needed for latest PyQt5
RUN apt update \
    && apt install -y --no-install-recommends tzdata libxkbcommon-x11-0

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

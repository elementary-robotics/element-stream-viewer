FROM elementaryrobotics/atom:v1.1.0

# libxkbcommon-x11 needed for latest PyQt5
RUN apt update \
    && apt install -y --no-install-recommends tzdata libxkbcommon-x11-0

ADD . /code

#
# Install python dependencies
#
WORKDIR /code

# Upgrade pip for latest PyQt5
RUN pip3 install --upgrade pip \
    && pip3 install --no-cache-dir -r requirements.txt

# Finally, specify the command we should run when the app is launched
RUN chmod +x launch.sh
CMD ["/bin/bash", "launch.sh"]

FROM elementaryrobotics/atom:v1.0.1

RUN apt update
RUN DEBIAN_FRONTEND=noninteractive apt install -y tzdata libopencv-dev

ADD . /code

#
# Install python dependencies
#
WORKDIR /code
# Upgrade pip for latest PyQt5
RUN pip3 install --upgrade pip
# Also needed for latest PyQt5
RUN sudo apt-get install -y --no-install-recommends libxkbcommon-x11-0
RUN pip3 install -r requirements.txt

# Finally, specify the command we should run when the app is launched
RUN chmod +x launch.sh
CMD ["/bin/bash", "launch.sh"]

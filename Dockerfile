FROM elementaryrobotics/atom

RUN apt update
RUN DEBIAN_FRONTEND=noninteractive apt install -y tzdata libopencv-dev

ADD . /code

#
# Install python dependencies
#
WORKDIR /code
RUN pip3 install -r requirements.txt

# Finally, specify the command we should run when the app is launched
RUN chmod +x launch.sh
CMD ["/bin/bash", "launch.sh"]

FROM elementaryrobotics/element-segmentation-base:ed62eff7f4fa3dbb3aa4cb80a7950dac1d42bb52

# Want to copy over the contents of this repo to the code
#	section so that we have the source
ADD . /code

#
# Install python dependencies
#
WORKDIR /code
RUN pip3 install -r requirements.txt

# Finally, specify the command we should run when the app is launched
RUN chmod +x launch.sh
CMD ["/bin/bash", launch.sh"]

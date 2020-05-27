## stream-viewer

### Build Status

[![CircleCI](https://circleci.com/gh/elementary-robotics/element-stream-viewer.svg?style=svg&circle-token=610bb3954b6e24ce2efe414dc90fb79d653abdde)](https://circleci.com/gh/elementary-robotics/element-stream-viewer)

### Overview
The stream-viewer element is a GUI tool used for viewing image data that is written to a stream.
It works with both color and depth streams and is a useful tool for testing and debugging computer vision algorithms.

![Inspect screenshot](assets/stream_viewer_screenshot.png)

### docker-compose configuration
In order to save images from stream-viewer, you must mount your local ~/Pictures directory to /Pictures.
This element also requires special flags to enable display forwarding.
```
  stream-viewer:
    image:elementaryrobotics/element-stream-viewer
    volumes:
      - type: volume
        source: shared
        target: /shared
        volume:
          nocopy: true
      - "~/Pictures:/Pictures"
      - "/tmp/.X11-unix:/tmp/.X11-unix:rw"
    environment:
      - "DISPLAY"
      - "QT_X11_NO_MITSHM=1"
    depends_on:
      - "nucleus"
```


### Usage
Since this element utilizes a GUI, we need to forward the display between Docker and the host machine.
This command will allow the root user in the container to have access to the X Server. Run this command on the host machine.

```shell
xhost +SI:localuser:root
```

Then start the element following the usual steps.


### Usage with realsense element
Start this element in conjunction with the realsense element.


### Usage with your own image streams
Currently, stream-viewer will list all available streams in the atom system, but can only view streams with data of a specific format. Specifically, by default this element expects binary data in a standard image format (any format supported by OpenCV's `imencode`/`imdecode` such as .tif, .jpeg, .png) under the "data" key in each stream entry.  However it is recommended to instead write the image data to the stream as an arrow-serialized array (2D array for black-and-white, 3D for color). Arrow arrays are faster and more memory-efficient than standard image formats.  Instead of encoding images, simply pass a numpy array under the "data" key to `entry_write` with `serializaton="arrow", and `stream-viewer` will correctly display the image.

This can be done in Python as follows

```python
#  Write an arrow-encoded entry to the "image" stream so that it can be displayed by stream-viewer
#  (img is a numpy array)
element.entry_write("image", {"data": img}, maxlen=30, serialization="arrow")

#  Write a tif-encoded entry so that can be displayed by stream-viewer
_, tif_img = cv2.imencode(".tif", img)
element.entry_write("image", {"data": tif_img.tobytes()}, maxlen=30, serialization=None)
```

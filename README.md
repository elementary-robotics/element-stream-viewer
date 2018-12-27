Expects a tif encoded image written to a stream with the key to the image as `data`
```
_, tif_img = cv2.imencode(".tif", img)
element.entry_write("img", {"data": tif_img.tobytes()}, maxlen=30)
```
This will allow the root user in the container to have access to the X Server.
```
xhost +SI:localuser:root
```

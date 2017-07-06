# cameraStreaming

## ----- Camera.py -----

This script open a (pyside) window with connect and quit buttons.
The connect button open a new (opencv) window ad stream the webcam of the pc in it.

### Display command line options:

```bash
python camera.py -h
```

### Next goals:

- make it handle piCamera of raspberryPi

### Long term goals:

- access to the camera from a distant raspberry pi (through wifi connection)

## ----- server.py -----

This script launches a python server. To access it, open your navigator and type:
- localhost:8888/index.py (server running on local)
- 192.168.0.XX:8888/index.py (server running on raspberryPi)

Type Ctrl-C to close it.

Comment: one line to change in server.py depending if the server is running locally or on raspberryPi (indicated in the code).

### Next goals:

- Solve bug on raspberryPi: for now, index.py is only displayed and not executed. though it is when the server run locally.

### Long term goals:

- Make an interface to send and receive information to/from the robot.

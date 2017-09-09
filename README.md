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

# Server
## ----- server_apache2.py -----
This script is runned as cgi under apache2 server. To access it, open your navigator and type:
192.168.0.XX:/cgi-bin/server_apache2.py (server running on raspberryPi)

## ----- listener.py -----
This script is runned as cgi under apache2 server and collects informations from server_apache2.py- It is charged automatically when you click on "submit" on the server_apache2 page.

## Installation:
Get apache2:
```
sudo apt-get install apache2
```
Modify the config file: /etc/apache2/conf-enabled/serve-cgi-bin.conf:
```
ScriptAlias /cgi-in/ /usr/lib/cgi-bin/            # Change to:  ScriptAlias /cgi-in/ /home/pi/hopiro/cgi-bin/ (folder where you will place your python code)
<Directory "usr/lib/cgi-bin">                     # Change to:  <Directory "/home/pi/hopiro/cgi-bin/">
             ... ...
              AddHandler cgi-script .py           # add this line (there is a blank between cgi-script and .py)
</Directory>
```
Restart apache2:
```
sudo service apache2 restart
```
Part of the instructions comes from https://www.raspberrypi.org/forums/viewtopic.php?f=28&t=155229#

### Next goals:

- Solve bug on raspberryPi: for now, index.py is only displayed and not executed. though it is when the server run locally.

### Long term goals:

- Make an interface to send and receive information to/from the robot.

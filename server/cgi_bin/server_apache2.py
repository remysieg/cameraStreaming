#!/usr/bin/python

import cgi
import cgitb
cgitb.enable()

form = cgi.FieldStorage()
print("Content-type: text/html; charset=utf-8\n")

print(form.getvalue("name"))

html = """<!DOCTYPE html>
<head>
    <title>HoPiRo</title>
</head>
<body>
    <form action="/cgi-bin/server_apache2.py" method="post">
        <input type="text" name="name" value="Votre nom" />
        <input type="submit" name="send" value="Envoyer information au serveur">
    </form>
</body>
</html>
"""

print(html)

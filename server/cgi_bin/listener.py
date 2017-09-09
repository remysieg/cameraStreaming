#!/usr/bin/python

import cgi
import cgitb
cgitb.enable()

form = cgi.FieldStorage()

name = form.getvalue('name')

print "Content-type:text/html\r\n\r\n"
print "<html>"
print "<head>"
print "<title>Hello - Second CGI Program</title>"
print "</head>"
print "<body>"
print "<h2>Hello %s</h2>" % (name)
print "</body>"
print "</html>"

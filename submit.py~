#!/usr/bin/env python

import sys
import pycurl
import StringIO

if len(sys.argv) != 2:
    print 'Usgage: %s <filename>' % sys.argv[0] 
    sys.exit()

user = 'esl'
pwd = '12345678'
base_url = 'http://cpre.kmutnb.ac.th/esl/share/photos_demo/'
script_filename = 'submit.php'
local_filename = sys.argv[1]

c = pycurl.Curl()
fout = StringIO.StringIO()
c.setopt( pycurl.WRITEFUNCTION, fout.write )
c.setopt( c.URL, base_url + script_filename )
c.setopt( c.HTTPPOST,[ 
  ("user", user),
  ("pwd", pwd), 
  ("photo", 
    (c.FORM_FILE, local_filename, 
     c.FORM_CONTENTTYPE, "image/jpeg")
   )
])

try:
    c.perform()
    resp_code = c.getinfo(pycurl.RESPONSE_CODE)
    resp_data = fout.getvalue()
    print resp_code, resp_data
except Exception as ex:
    print 'Curl error:', ex

c.close()


#!/usr/bin/env python
#coding=utf-8

# store

import socket
from datetime import datetime
from ftp_upload import ftp_upload

def save_to_file(result):
    print "Saving result...."
    hostname = socket.gethostname()
    file_tail = datetime.now().strftime('%Y-%m-%d-%H') + '.txt'
    file_path = 'output/'
    file_name = hostname + '-result' + file_tail
    file_result = open(file_path + file_name,'w')
    for record in result:
        line = ';'.join(record) + '\n'
        file_result.write(line)
    file_result.close()
    try:
        ftp_upload(file_name, file_path)
    except:
        print "Upload Fail!"
    print "Save Complete!"

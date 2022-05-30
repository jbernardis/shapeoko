import os
import pysftp

fn = "c:\\Users\\jeff\\git\\shapeoko\\openscad\\buttonbezel.scad"
bn = os.path.basename(fn)
print("Base name (%s)" % bn)

with pysftp.Connection('192.168.1.127', username="jeff", password="5braxton") as sftp:
    with sftp.cd("shapeoko"):
        if sftp.isfile(bn):
            print("File exists - overwriting")

        msg = sftp.put(fn)
        print(msg)

import wx
import pysftp
import os
import datetime

modeString = [
    "---", "--x", "-w-", "-wx", "r--", "r-x", "rw-", "rwx"
]

def getMode(md):
    mw = md % 0x08;
    mg = int(md/8) % 0x08
    mo = int(md/64) % 0x08
    return "%s %s %s" % (modeString[mo], modeString[mg], modeString[mw])

class ShapeokoFile:
    def __init__(self, name, mtime, mode, size):
        self.filename = name
        self.mtime = mtime
        self.mode = mode
        self.size = size

class FileList:
    def __init__(self, parent, ipname, user, password):
        self.parent = parent
        self.ipname = ipname
        self.user = user
        self.password = password
        self.refresh()

    def uploadFiles(self, fl):       
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None 

        uploadList = []
        with pysftp.Connection(self.ipname, username=self.user, password=self.password, cnopts=cnopts) as sftp:
            with sftp.cd("shapeokodata"):
                for fn in fl:
                    bn = os.path.basename(fn)
                    if sftp.exists(bn):
                        dlg = wx.MessageDialog(self.parent,  "File \"%s\" already exists.\nPress YES to upload or NO to skip" % bn, "File already exists",
                            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
                        rc = dlg.ShowModal()
                        dlg.Destroy()
                        if rc == wx.ID_NO:
                            continue

                    sftp.put(fn)
                    uploadList.append(bn)

        self.refresh()

        dlg = wx.MessageDialog(self.parent,  "Files successfully uploaded:\n%s" % "\n".join(uploadList), "Files Uploaded",
                wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def deleteFiles(self, fl):
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None 

        with pysftp.Connection(self.ipname, username=self.user, password=self.password, cnopts=cnopts) as sftp:
            with sftp.cd("shapeokodata"):
                for fn in fl:
                    sftp.remove(fn)

        self.refresh()

        dlg = wx.MessageDialog(self.parent,  "Files successfully deleted:\n%s" % "\n".join(fl), "Shapeoko Files Deleted",
                wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def refresh(self):
        self.fileList = []

        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None 

        sftp = pysftp.Connection(self.ipname, username=self.user, password=self.password, cnopts=cnopts)
        sftp.chdir("shapeokodata")
        for attr in sftp.listdir_attr():
            ts = datetime.datetime.fromtimestamp(attr.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            mode = getMode(attr.st_mode)
            self.fileList.append(ShapeokoFile(attr.filename, ts, mode, "%d" % attr.st_size))
        sftp.close()

    def count(self):
        return len(self.fileList)

    def getFileName(self, fx):
        if fx < 0 or fx >= self.count():
            return None

        return self.fileList[fx].filename

    def getFileByPosition(self, fx):
        if fx < 0 or fx >= self.count():
            return None

        return self.fileList[fx]

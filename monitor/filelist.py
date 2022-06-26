import pysftp

class FileList:
    def __init__(self, ipname, user, password):
        self.ipname = ipname
        self.user = user
        self.password = password
        self.files = []
        self.refresh()

    def refresh(self):
        self.files = []
        self.__fx = 0

        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None 

        with pysftp.Connection(self.ipname, username=self.user, password=self.password, cnopts=cnopts) as sftp:
            with sftp.cd("shapeokodata"):
                for attr in sftp.listdir_attr():
                    self.files.append(attr.filename)
 
    def __len__(self):
        return len(self.files)

    def __iter__(self):
        self.__fx = 0
        return self
 
    def __next__(self):
        if self.__fx >= len(self):
            raise StopIteration
        else:
            rv = self.files[self.__fx]
            self.__fx += 1
            return rv

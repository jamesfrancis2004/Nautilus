class File:


    def __init__(self, name, user, req_perms, parent):
        self.name = name
        self.owner_user = user
        self.req_perms = req_perms
        self.parent = parent

    def __repr__(self):
        return self.name

    def is_file(self):
        return True


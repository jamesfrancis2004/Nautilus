class Directory:


    def __init__(self, name, parent, user, req_perms):
        self.name = name
        self.directories = {"..": parent, ".": self}
        self.files = {}
        self.owner_user = user
        self.req_perms = req_perms
        self.parent = parent

    def __repr__(self):
        return self.name

    def is_file(self):
        return False

    def is_empty(self):
        if len(self.files) == 0 and len(self.directories) == 2:
            return True

        return False




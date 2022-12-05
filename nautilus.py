from File import File
from Directory import Directory
from User import User

USER_READ = 1
USER_WRITE = 2
USER_EX = 3
GROUP_READ = 4
GROUP_WRITE = 5
GROUP_EX = 6
PERM_DENIED = -1
# Constants for positional parameters for checking perms

class System:


    def __init__(self, curr_user, home_dir):
        self.whitespace = set([" ", "\t", "\n"])
        self.commands = {"exit": self.exit_system,
                         "pwd": self.pwd,
                         "cd": self.change_dir,
                         "mkdir": self.make_dir,
                         "touch": self.touch_file,
                         "cp": self.copy,
                         "mv": self.move,
                         "rm": self.remove_file,
                         "rmdir": self.remove_dir,
                         "chmod": self.chmod,
                         "chown": self.chown,
                         "adduser": self.add_user,
                         "deluser": self.del_user,
                         "su": self.switch_user,
                         "ls": self.list_info}

        # Dictionary to store all valid args and their function as values.
        # If valid arg is given the function corresponding to arg is run

        self.VALID_COMMAND_CHARS = set(['a', 'b', 'c', 
                                        'd', 'e', 'f', 
                                        'g', 'h', 'i',
                                        'j', 'k', 'l',
                                        'm', 'n', 'o',
                                        'p', 'q', 'r', 
                                        's', 't', 'u',
                                        'v', 'w', 'x',
                                        'y', 'z', '0',
                                        '1', '2', '3', 
                                        '4', '5', '6',
                                        '7', '8', '9',
                                        'A', 'B', 'C',
                                        'D', 'E', 'F',
                                        'H', 'I', 'L',
                                        'M', 'N', 'O',
                                        'P', 'Q', 'R',
                                        'S', 'T', 'U',
                                        'V', 'Q', 'R',
                                        'S', 'W', 'X',
                                        'Y', 'Z', '_',
                                        '.', '-', '/',
                                        '+', '=', ' '])

        
        self.home_user = curr_user
        self.users = {f"{curr_user.name}" : curr_user}
        self.master_user = curr_user
        self.curr_user = curr_user
        self.working_dir = home_dir
        self.home_dir = home_dir

    def get_current_path(self):
        curr_path = ""
        temp_dir = self.working_dir
        if self.working_dir == self.home_dir:
            return "/"
        while (temp_dir.parent != None):
            curr_path = f"/{temp_dir.name}" + curr_path
            temp_dir = temp_dir.parent

        return curr_path
        # Function returns full string path of directory
        # If directory is root it returns / 
        # Otherwise it loops until the root directory

    def check_single_perm(self, perm_pos, obj):
        if (self.curr_user == self.home_user):
            return True

        elif self.curr_user == obj.owner_user:
            if (obj.req_perms[perm_pos] == '-'):
                return False
        else:
            if (obj.req_perms[perm_pos+3] == '-'):
                return False

        return True

        # Checks for user permission
        # Returns True if user can access file

    def check_ancestral_execute_perm(self, temp_dir):
        while (temp_dir != None):
            if not self.check_single_perm(USER_EX, temp_dir):
                return False

            temp_dir = temp_dir.parent
        return True

    # Checks if ancestor directory have execute perm
    # Returns true if all ancestor directories contain exe perm

    def check_valid_chars(self, args_provided):
        for i in args_provided:
            for j in i:
                if j not in self.VALID_COMMAND_CHARS:
                    return False

        return True
    # Checks the arguments are all valid characters


    def separate_cmdline_args(self, args_provided, delimiter):
        arguments = []
        curr_command = ""
        string_identifier_found = False
        command_found = False
        closing_identifier=""
        for i in args_provided:
            if i in delimiter and not command_found:
                continue

            if i == '"' and not string_identifier_found:
                string_identifier_found = True
                closing_identifier = '"'
                continue

            elif i == "<" and not string_identifier_found:
                string_identifier_found = True
                closing_identifier = ">"
                continue

            if i == closing_identifier:
                string_identifier_found = False
                continue

            elif i not in delimiter or string_identifier_found:
                command_found = True
                curr_command += i

            if i in delimiter and not string_identifier_found and command_found:
                command_found = False
                arguments.append(curr_command)
                curr_command = ""
            
        if (command_found):
            arguments.append(curr_command)

        if (string_identifier_found):
            print(f"Expected a closing {closing_identifier}")
            return None

        return arguments

    # Generic parser. 
    # Seperates arguments by whitespace characters.
    # If angled or quotation marks are given read until closing identifier.


    
    def read_user_input(self):
        while True: 
            cmdline_input = input(f"{self.curr_user.name}:{self.get_current_path()}$ ")
            args = self.separate_cmdline_args(cmdline_input, self.whitespace)
            if (args == None):
                continue
            
            if (len(args) == 0):
                continue

            if (args[0] in self.commands):
                self.commands[args[0]](args[1:])

            else:
                print(f"{args[0]}: Command not found")
        # Function asks for user input. Will continue asking until exit command
        # Hashtable of commands and function pointers is used to call specified command.
        # If command entered is not in the hashtable then prints invalid input
            
    def pwd(self, args):
        if (len(args) != 0):
            print(f"pwd: Invalid syntax")
            return

        print(f"{self.get_current_path()}")
        
        # Prints working dir using get_current_path method

    def return_dest_dir(self, raw_path, full_path_mode=False, p_mode=False):
        split_path = self.separate_cmdline_args(raw_path, set(["/"]))
        if len(split_path) == 0:
            return raw_path, self.home_dir
        end = len(split_path) if full_path_mode else len(split_path) - 1
        directory_structure = split_path[0:end] 
        dest_obj_name = split_path[len(split_path) - 1] if not full_path_mode else None
        temp_dir = self.home_dir if raw_path[0] == "/" else self.working_dir
        # Differentiates between CD and rest of commands
        
        for i in directory_structure:
            if i in temp_dir.directories:
                temp_dir = temp_dir.directories[i]

            elif p_mode:
                if not self.check_ancestral_execute_perm(temp_dir):
                    return PERM_DENIED, PERM_DENIED
                if not self.check_single_perm(USER_WRITE, temp_dir):
                    return PERM_DENIED, PERM_DENIED

                new_dir = Directory(i, temp_dir, self.curr_user, "drwxr-x")
                temp_dir.directories.update({i: new_dir})
                temp_dir = new_dir

            elif i in temp_dir.files:
                return dest_obj_name, temp_dir.files[i]

            else:
                return dest_obj_name, None

        return dest_obj_name, temp_dir

        # Returns the directory the file is in and the file name.
        # The function this is passed back to then does all the relevant error checks.

    def touch_file(self, args):
        if (len(args) > 1 or len(args) == 0 or not self.check_valid_chars(args)):
            print(f"touch: Invalid syntax")
            return

        file_name, dest_dir = self.return_dest_dir(args[0])

        if dest_dir == None:
            print("touch: Ancestor directory does not exist")
            return

        elif dest_dir.is_file():
            print("touch: Ancestor directory does not exist")
            return

        elif not self.check_ancestral_execute_perm(dest_dir):
            print("touch: Permission denied")
            return

        elif not self.check_single_perm(USER_WRITE, dest_dir):
            print("touch: Permission denied")
            return

        dest_dir.files.update({file_name: File(file_name, self.curr_user, "-rw-r--", dest_dir), })

        # Creates a file in the directory specified in the command.
        # All relevant error checks are performed in the if statement.

    def change_dir(self, args):
        if (len(args) != 1 or not self.check_valid_chars(args)):
            print(f"cd: Invalid syntax")
            return

        dest_dir = self.return_dest_dir(args[0], True)[1]

        if dest_dir == None:
            print("cd: No such file or directory")
  
        elif dest_dir.is_file():
            print("cd: Destination is a file")

        elif not self.check_ancestral_execute_perm(dest_dir):
            print("cd: Permission denied")

        else:
            self.working_dir = dest_dir

        # Changes directory to the directory returend by self.return_dest_dir
        # Performs error checks on returned directory.
        # If works out sets working dir to returned dir

    
    def make_dir(self, args):
        p_mode = False
        if (len(args) > 2 or len(args) < 1 or not self.check_valid_chars(args)):
            print(f"mkdir: Invalid syntax")
            return 

        if (len(args) == 2):
            if (args[0] != "-p"):
                print(f"mkdir: Invalid syntax")
                return
            p_mode = True

        new_dir_name, dir_new_dir_in = self.return_dest_dir(args[len(args) - 1],
                                              False,
                                              p_mode)

        if dir_new_dir_in == PERM_DENIED:
            print("mkdir: Permission denied")
            return
        elif not isinstance(dir_new_dir_in, Directory):
            print("mkdir: Ancestor directory does not exist")
        elif (new_dir_name in dir_new_dir_in.directories 
              or new_dir_name in dir_new_dir_in.files) and not p_mode:
            print("mkdir: File exists")
        elif not self.check_single_perm(USER_WRITE, dir_new_dir_in):
            print("mkdir: Permission denied")
        else:
            dir_new_dir_in.directories.update(
                                            {new_dir_name: Directory(new_dir_name,
                                                           dir_new_dir_in,
                                                           self.curr_user,
                                                           "drwxr-x")})

        # Makes a directory at path specified. 
        # Checks for p-mode given by the "-p" flag.
        # Perfroms relevant error checks on directory returend.
        # If checks out creates a new directory with all the relevant properties.


    def move(self, args):
        if (len(args) != 2 or not self.check_valid_chars(args)):
            print(f"mv: Invalid syntax")
            return 

        src_file_name, src_dir_in = self.return_dest_dir(args[0])
        dest_file_name, dest_dir_in = self.return_dest_dir(args[1])

        if src_dir_in == None or dest_dir_in == None:
            print("mv: No such file or directory")

        elif src_dir_in.is_file() or dest_dir_in.is_file():
            print("mv: No such file or directory")
            return

        elif (not self.check_ancestral_execute_perm(src_dir_in) 
            or not self.check_ancestral_execute_perm(dest_dir_in)):
            print("mv: Permission denied")
            return 


        elif dest_file_name in dest_dir_in.directories:
            print("mv: Destination is a directory")
            return


        elif src_file_name not in src_dir_in.files:
            if src_file_name in src_dir_in.directories:
                print("mv: Source is a directory")
            else:
                print("mv: No such file")


        elif (not self.check_single_perm(USER_WRITE, src_dir_in) 
             or not self.check_single_perm(USER_WRITE, dest_dir_in)):
            print("mv: Permission denied")
        elif dest_file_name in dest_dir_in.files:
            print("mv: File exists")
        else:
            dest_dir_in.files.update({dest_file_name : src_dir_in.files[src_file_name]})
            dest_dir_in.files[dest_file_name].name = dest_file_name
            src_dir_in.files.pop(src_file_name)

        # Moves a file from source to destination.
        # self.return_dest_dir returns both src and dest directories.
        # Does all relevant error checks and if checks out pops file from src and moves to dest.


    def copy(self, args):
        if (len(args) != 2 or not self.check_valid_chars(args)):
            print(f"cp: Invalid syntax")
            return

        src_file_name, src_dir_in = self.return_dest_dir(args[0])
        dest_file_name, dest_dir_in = self.return_dest_dir(args[1])

        if src_dir_in == None or dest_dir_in == None:
            print("cp: No such file or directory")


        elif src_dir_in.is_file() or dest_dir_in.is_file():
            print("cp: No such file or directory")

        elif (not self.check_ancestral_execute_perm(src_dir_in)
              or not self.check_ancestral_execute_perm(dest_dir_in)):
            print("cp: Permission denied")


        elif dest_file_name in dest_dir_in.directories:
            print("cp: Destination is a directory")


        elif src_file_name not in src_dir_in.files:
            if src_file_name in src_dir_in.directories:
                print("cp: Source is a directory")
            else:
                print("cp: No such file")
            return

        elif (not self.check_single_perm(USER_READ, src_dir_in.files[src_file_name])
                or not self.check_single_perm(USER_WRITE, dest_dir_in)):
            print("cp: Permission denied")

        elif dest_file_name in dest_dir_in.files:
            print("cp: File exists")

        else:
            new_file = File(dest_file_name,
                            self.curr_user,
                            src_dir_in.files[src_file_name].req_perms,
                            dest_dir_in)
            dest_dir_in.files.update({dest_file_name : new_file})

        # The copy command copies a file from one directory to another.
        # Uses almost the same method as move except the final file in src is not popped.

    def remove_file(self, args):
        if (len(args) != 1 or not self.check_valid_chars(args)):
            print(f"rm: Invalid syntax")
            return

        targ_file_name, dest_parent = self.return_dest_dir(args[0])

        if dest_parent == None:
            print("rm: No such file")
        elif not self.check_ancestral_execute_perm(dest_parent):
            print("rm: Permission denied")
        elif not self.check_single_perm(USER_WRITE, dest_parent):
            print("rm: Permission denied")
        elif targ_file_name in dest_parent.directories:
            print("rm: Is a directory")
        elif targ_file_name not in dest_parent.files:
            print("rm: No such file")
        else:
            if not self.check_single_perm(USER_WRITE, dest_parent.files[targ_file_name]):
                print("rm: Permission denied")
            else:
                dest_parent.files.pop(targ_file_name)

        # This function uses the return_dest_dir function to find target file for deletion
        # The main purpose of the function is to check for errors.
        # If no errors are detected in command input the functon removes the file from dict

    def check_if_pwd(self, directory):
        temp_dir = self.working_dir
        while temp_dir != None:
            if temp_dir == directory:
                return True

            temp_dir = temp_dir.parent

        return False

    # This function is for remove dir.
    # It checks that the directory specified is not the current working dir
    # Or the current working dirs ancestor.

    def remove_dir(self, args):
        if (len(args) != 1 or not self.check_valid_chars(args)):
            print(f"rmdir: Invalid syntax")
            return 

        dest_dir_name, dest_parent = self.return_dest_dir(args[0])

        if dest_parent == None:
            print("rmdir: Not a directory")
            return

        elif dest_dir_name == "/" and dest_parent == self.home_dir:
            temp_dir = self.home_dir

        elif not self.check_ancestral_execute_perm(dest_parent):
            print("rmdir: Permission denied")
            return

        elif dest_dir_name not in dest_parent.directories:
            if dest_dir_name in dest_parent.files:
                print("rmdir: Not a directory")
            else:
                print("rmdir: No such file or directory")
            return
        elif not self.check_single_perm(USER_WRITE, dest_parent):
            print("rmdir: Permission denied")
            return
        else:
            temp_dir = dest_parent.directories[dest_dir_name]

        if temp_dir.is_empty():
            if self.check_if_pwd(temp_dir):
                print("rmdir: Cannot remove pwd")
                return
            dest_parent.directories.pop(dest_dir_name)
        else:
            print("rmdir: Directory not empty")

        # Function uses the return_dest_dir function to find target file for deletion
        # If statement block checks for all relevant errors. 
        # Function also checks for whether target directory is empty.
        # If all error checks are performed and no errors found the directory is deleted.

    def change_ownership(self, file_obj, new_owner):
        file_obj.owner_user = new_owner

        # Can be specified as function arg in recursive to change file owner
        # Also can be called standalone to change file owner of single file

    def recursive(self, func_mod_obj, **kwargs):
        func_mod_obj(**kwargs)
        if kwargs["file_obj"].is_file():
            return
        else:
            temp_file = kwargs.pop("file_obj")
            for i in temp_file.directories.keys():
                if i[0] == ".":
                    continue
                else:
                    target_file = temp_file.directories[i]
                self.recursive(func_mod_obj, file_obj=target_file, **kwargs)
            for i in temp_file.files.values():
                self.recursive(func_mod_obj, file_obj=i,  **kwargs)

        # Generic recursive function.
        # Takes function as first function parameter and then modifies files accordingly
        # Uses **kwargs keyword to store values as dictionay for either the change_ownership
        # or the change_permissions function.
        # Only python function I've ever written thats as unreadable as C.

    
    def change_permissions(self, file_obj, perm_dict):
        if self.curr_user != self.home_user and file_obj.owner_user != self.curr_user:
            print("chmod: Operation not permitted")
            return

        for perm_type, new_perm in zip(perm_dict.keys(), perm_dict.values()):
            if perm_type == 'u':
                positions = [[USER_READ], [USER_WRITE], [USER_EX]]
            elif perm_type == 'o':
                positions = [[GROUP_READ], [GROUP_WRITE], [GROUP_EX]]
            elif perm_type == 'a':
                positions = [(USER_READ, GROUP_READ),
                             (USER_WRITE, GROUP_WRITE),
                             (USER_EX, GROUP_EX)]

            for idx, key in enumerate(new_perm.keys()):
                if new_perm[key] == True:
                    perm = key
                elif new_perm[key] == False:
                    perm = "-"
                else:
                    continue

                for i in positions[idx]:
                    temp_list = list(file_obj.req_perms)
                    temp_list[i] = perm
                    file_obj.req_perms = "".join(temp_list)

        # Changes the perms for a file using the perm dict. 
        # Checks for all relevant errors then changes perms.

    def chmod(self, args):
        recursive_mode = False
        perms={"u": {"r" : None, "w": None, "x": None},
               "o": {"r": None, "w": None, "x": None},
               "a": {"r": None, "w": None, "x": None}}
        valid_perm_types = set(["u", "o", "a"])
        symbolic_operators = set(["+", "-", "="]) 
        valid_perms = set(["r", "w", "x"])
        format_string_pos = 0
        if len(args) > 3 or len(args) < 2 or not self.check_valid_chars(args):
            print(f"chmod: Invalid syntax")
            return

        if (args[0] == "-r"):
            recursive_mode = True
            format_string_pos = 1

        format_string = args[format_string_pos]
        idx = 0
        symbolic_found = False
        perm_types = []
        perm_dict = {}
        for idx, i in enumerate(format_string):
            if i in symbolic_operators:
                symbolic_found = True
                if i == "=":
                    operator = True
                    command_dict = {"r": False, "w": False, "x": False}
                elif i == "-":
                    operator = False
                    command_dict = {"r": None, "w": None, "x": None}
                elif i == "+":
                    operator = True
                    command_dict = {"r": None, "w": None, "x": None}
                perms = format_string[idx+1:]
                break
                    
            elif i not in valid_perm_types:
                print("chmod: Invalid mode")
                return 
            
            else:
                perm_types.append(i)

        if (not symbolic_found):
            print("chmod: Invalid mode")
            return

        for i in perms:
            if i not in valid_perms:
                print("chmod: Invalid mode")
                return
            
            command_dict[i] = operator
        
        for i in perm_types:
            perm_dict.update({i: command_dict})


        dest_file_name, dest_parent = self.return_dest_dir(args[len(args) - 1])

        if dest_parent == None:
            print("chmod: No such file or directory")
            return

        elif dest_file_name == "/" and dest_parent == self.home_dir:
            target_file = self.home_dir

        elif dest_file_name not in dest_parent.directories and dest_file_name not in dest_parent.files:
            print("chmod: No such file or directory")
            return

        elif not self.check_ancestral_execute_perm(dest_parent):
            print("chmod: Permission denied")
            return
        else:
            if dest_file_name in dest_parent.directories:
                target_file = dest_parent.directories[dest_file_name]
            else:
                target_file = dest_parent.files[dest_file_name]


        if recursive_mode:
            self.recursive(self.change_permissions,
                           file_obj = target_file, 
                           perm_dict = perm_dict,
                          )
        else:
            self.change_permissions(file_obj = target_file, 
                                    perm_dict = perm_dict, 
                                    )
    
    # Filters and reads the command line input from chmod.
    # Error checks for all relevant errors.
    # Checks if the recursive flag is included in command. 
    # Uses the self.change_permissions function if recursive not included.
    # Other self.recursive function is used with change_permissions as an argument.

    def chown(self, args):
        recursive_mode = False 
        if len(args) != 2 and len(args) != 3 or not self.check_valid_chars(args):
            print(f"chown: Invalid syntax")
            return
        elif self.curr_user != self.home_user:
            print(f"chown: Operation not permitted")
            return
        if (len(args) == 3):
            if args[0] == "-r":
                recursive_mode = True
            else:
                print(f"chown: Invalid syntax")
                return

        user = args[len(args) - 2]
        path = args[len(args) - 1]
        if user not in self.users:
            print(f"chown: Invalid user")
            return

        dest_file, dest_parent = self.return_dest_dir(path)
        if dest_parent == None:
            print("chown: No such file or directory")
        elif dest_file == "/" and dest_parent == self.home_dir:
            temp_file = self.home_dir
        elif dest_file in dest_parent.directories:
            temp_file = dest_parent.directories[dest_file]
        elif dest_file in dest_parent.files:
            temp_file = dest_parent.files[dest_file]
        else:
            print("chown: No such file or directory")
            return
        
        if recursive_mode:
            self.recursive(self.change_ownership, file_obj=temp_file, new_owner=self.users[user]) 
        else:
            self.change_ownership(file_obj=temp_file, new_owner=self.users[user])

        # Changes the ownership of files to the specified user.
        # Must be root user for functio to work.
        # If "-r" flag is specified then change ownership recursively
        # Checks for relevant errors in cmdline arguments. 


    def add_user(self, args):
        if (len(args) != 1 or not self.check_valid_chars(args)):
            print(f"adduser: Command not found")
            return

        if args[0] in self.users:
            print("adduser: The user already exists")
            return

        elif self.curr_user != self.home_user:
            print("adduser: Operation not permitted")
            return 

        self.users.update({args[0]: User(args[0])})
        
        # Add specified user to the system users
        # Checks for all relevant errors.

    def del_user(self, args):
        if (self.curr_user != self.home_user):
            print("deluser: Operation not permitted")
            return 

        if (len(args) != 1 or not self.check_valid_chars(args)):
            print(f"deluser: Command not found")
            return
        

        if (args[0] == "root"):
            print("WARNING: You are just about to delete the root account")
            print("Usually this is never required as it may render the whole system unusable")
            print("If you really want this, call deluser with parameter --force")
            print("(but this `deluser` does not allow `--force`, haha)")
            print("Stopping now without having performed any action")
            return 

        elif (args[0] in self.users):
            self.users.pop(args[0])

        else:
            print("deluser: The user does not exist")

        # Deletes specified user from the system.
        # If root is specified as arg block from happening
        # If no user matches specified name print corresponding error message
    
    def switch_user(self, args):
        if (len(args) == 0):
            self.curr_user = self.home_user

        elif (len(args) == 1):
            if not self.check_valid_chars(args[0]):
                print("su: Invalid syntax")
            elif (args[0] in self.users):
                self.curr_user = self.users[args[0]]
            else:
                print(f"su: Invalid user")
        else:
            print(f"su: Invalid syntax")

        # Switches the current user to the specified user
        # If user does not exist print corresponding error message
        # If no user arg is specified switches user to root

    def list_contents(self, file_obj, raw_path="", a=False, d=False, l=False):
        if d:
            if raw_path == "":
               if (not a):
                   return 

               raw_path = '.'
            else:
                if (not a):
                    if raw_path[0] == ".":
                        return
            # Checks whether current dir is working dir
            # if is then directory name is "." to indicate current directory
            if l:
                print(f"{file_obj.req_perms} {file_obj.owner_user} {raw_path}")
            else:
                print(f"{raw_path}")

            return 

        if not file_obj.is_file():
            all_objects = []
            for i in file_obj.directories.keys(): 
                if (not a):
                    if (i[0] != '.'):
                        all_objects.append(i)
                else:
                    all_objects.append(i)

            for i in file_obj.files.keys(): 
                if (not a):
                    if (i[0] != '.'):
                        all_objects.append(i)
                else:
                    all_objects.append(i)

            all_objects.sort()
            for i in all_objects:
                if i in file_obj.directories:
                    obj = file_obj.directories[i]
                else:
                    obj = file_obj.files[i]
                if l:
                    print(f"{obj.req_perms} {obj.owner_user} {i}")
                else:
                    print(i)

        else:
            if (not a):
                if raw_path[0] == ".":
                    return

            if l:
                print(f"{file_obj.req_perms} {file_obj.owner_user} {raw_path}")
            else:
                print(raw_path)

    # Lists the contents of a directory or prints file name
    # Changes output based on whether a, d, or l command is provided
    
    def list_info(self, args):
        flags = {"-a": False, "-d": False, "-l": False}
        if (len(args) < 0 or len(args) > 4 or not self.check_valid_chars(args)):
            print(f"ls: Invalid syntax")
            return 

        if (len(args) == 0):
            self.list_contents(self.working_dir)
            return

        if args[len(args) - 1][0] == "-":
            dest_dir = self.working_dir
            end = len(args)
            raw_path = ""
        else:
            dest_dir = self.return_dest_dir(args[len(args) - 1], True)[1]
            end = len(args) - 1
            raw_path = args[end]

        for idx, i in enumerate(args):
            if idx == end:
                break
            if i in flags:
                flags[i] = not(flags[i])
            else:
                print(f"ls: Invalid syntax")
                return
        if (dest_dir == None):
            print("ls: No such file or directory")
        elif (not self.check_single_perm(USER_READ, dest_dir)):
            print("ls: Permission denied")
        elif (not self.check_ancestral_execute_perm(dest_dir.parent)):
            print("ls: Permission denied")
        else:
            if dest_dir.is_file():
                if (not self.check_single_perm(USER_READ, dest_dir.parent)):
                    print("ls: Permission denied")
                    return
            else:
                if flags["-d"]:
                    if (not self.check_single_perm(USER_READ, dest_dir.parent)
                        or not self.check_single_perm(USER_READ, dest_dir)):
                        print("ls: Permission denied")
                        return
                    elif (not self.check_single_perm(USER_READ, dest_dir)):
                        print("ls: Permission denied")
                        return

            flags= list(flags.values())
            self.list_contents(dest_dir, raw_path, *flags)

        # Error checks for what was entered into the ls command
        # If no errors reported calls the list_contents function to list the dir
        # Checks for all relevant flags and provides those flags to list_contents function.

    def exit_system(self, args_given):
        if len(args_given) != 0:
            print("exit: Invalid syntax")
            return
        print(f"bye, {self.curr_user}")
        exit()
        # Function exits the program

def main():
    root_user = User("root")
    root_dir = Directory("/", None, root_user, "drwxr-x")
    root_dir.directories[".."] = root_dir
    cmdlet = System(root_user, root_dir)
    cmdlet.read_user_input()
    # Sets up all the relevant starting arguments for function then runs read_user_input

main()

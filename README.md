# Nautilus

Nautilus is a terminal interface written in python that acts to emulate the linux command line.
Current commands supported in nautilus are the following:

### `exit`
- Quits the program

### `pwd`
- Prints the name of current working virtual directory.


### `cd <dir>`
- Changes the working directory to '<dir>'

### `mkdir [-p] <dir>`
- Create the directory `<dir>`, if `<dir>` does not already refer to a file or directory.
- If `-p` is specified create full directory structure given by `<dir>`

### `touch <file>`
- Creates a new file

### `cp <src> <dst>`
- Copy a `<src>` to a file `<dst>`

### `mv <src><dst> `
- Moves a `<src>` to a file `<dst>`

### `rm <path>`
- Removes a file at `<path>`

### `rmdir <dir>`
- Removes a directory at `<dir>`.

### `chmod [-r] <s> <path>`
- Changes file or directory permissions to `<s>` on `<path>`
- If `-r` flag is given this is completed recursively from directory to base file

### `chown [-r] <user> <path>`
- Changes the file or directory owner at `<path>` to `<user>`
- If `-r` flag is given this is completed recursively from directory to base file

### `adduser <user>`
- Adds a user to the system

### `deluser <user>`
- Removes a user from the system.

### `su <user>`
- Switches the current effective user to `<user>`

### `ls [-a] [-d] [-l] [path]`
- Lists the information about <path>. Sort entries alphabetically.
- If `-a` is not specified, ommit entries starting with `.` in the output.
- If `-a` is specified, do not ommit entries starting with `.` in the output.
- If `-l` is not specified, use simple format, e.g. file or directory name.
- If `-l` is specified, use a long listing format.


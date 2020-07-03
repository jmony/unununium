import uuu
import vfs
import sys

def shell( *args ):
    '''shell

Execute a minimalistic shell.
'''
    def parse_tokens( tokens ):
        if not tokens:
            return
        command = globals().get( tokens[0] )
        if not callable(command):
            print 'no such command:', tokens[0]
        else:
            command( *tokens[1:] )

    if not args:
        print 'run "help" for help. Run "reboot" to reboot cleanly when done.'
        try:
            while True:
                line = raw_input( 'uuu %s $ ' % uuu.root_vfs.cwd )
                parse_tokens( line.split() )
        except (EOFError, KeyboardInterrupt):
            return
    else:
        parse_tokens( args )


def echo( *args ):
    '''echo

Have the computer mock you.
'''
    print ' '.join(args)


def exit( *args ):
    '''exit

Exit the shell.
'''
    raise KeyboardInterrupt


def pwd( *args ):
    '''pwd

Print the current working directory.
'''
    print uuu.root_vfs.cwd


def cat( *args ):
    '''cat FILE

Print the contents of FILE.
'''
    if not args:
        print "I'd make it cat stdin, but you could not type ^D to stop it."
        return
    for filename in args:
        f = file(filename)
        sys.stdout.write( f.read() )
        f.close()


def ls( *args ):
    '''ls

List the contents of the current directory. It is normal to see a name listed
multiple times.
'''
    if args:
        print 'ls takes no arguments'
        return
    files = []
    for dir in uuu.root_vfs.locate_nodes( uuu.root_vfs.cwd ):
        try:
            dir = dir.opendir()
        except vfs.FSLimitError:
            continue
        try:
            files.extend(list(dir))
        finally:
            dir.close()
    files.sort()
    for file in files:
        print file


def cd( *args ):
    '''cd DIR

Change the current working directory to DIR.
'''
    if len(args) != 1:
        print 'usage: cd DIR'
        return
    dir = args[0]
    try:
        uuu.root_vfs.cwd = dir
    except vfs.NoSuchNodeError:
        print 'cd: node %r does not exist' % args[0]


def touch( *args ):
    '''touch FILE [...]

Create FILE if it does not exist.
'''
    if not args:
        print 'usage: touch FILE [...]'
        return
    for filename in args:
        try:
            file( filename, 'w' ).close()
        except IOError, x:
            print 'can not touch %r: %r' % (filename, x)


def mount( *args ):
    '''mount DEVICE MOUNTPOINT TYPE [OPTIONS]

Mount DEVICE at MOUNTPOINT with filesystem driver TYPE with optional OPTIONS.
DEVICE is usually a path to a device node, like /dev/floppy/0. MOUNTPOINT may
be any valid path, although filesystem are by convention mounted under
/vol/NAME, then "bind" is used to attach them to other places. Currently
supported TYPEs are "ramfs" and "ext2". OPTIONS is an arbitrary string passed
to the FS driver. Ext2 recognizes "ro" to mount readonly, which is required
when mounting an ATA device, since the ATA driver does not support writing.
'''
    if len(args) != 3 and len(args) != 4:
        print 'usage: mount DEVICE MOUNTPOINT TYPE [OPTIONS]'
        return

    uuu.root_vfs.mount( *args )


def bind( *args ):
    '''bind NODE [...] TARGET

Bind NODE(s) to TARGET. The list of nodes may be any number of existing
filesystem nodes. Target may be any valid path. Binding nodes is simular to
hardlinking, except that it's done at the VFS layer, not the physical FS layer.
Consequently, binds may cross physical filesystems. Furthermore, Unununium
supports filesystem unions, so that multiple nodes may be bound to the same
path. For example, two physical filesystems mounted on /vol/a and /vol/b may
both be attached to the root.
'''
    if len(args) < 2:
        print 'usage: bind NODE [...] TARGET'
        return

    target = args[-1]
    args = args[:-1]
    nodes = []
    for path in args:
        nodes.extend( uuu.root_vfs.locate_nodes(path) )
    uuu.root_vfs.bind( nodes, target )


def help( *args ):
    '''help [TOPIC]

Get help on TOPIC, or print a summary if run with no arguments.
'''
    if len(args) == 1:
        try:
            doc = globals()[args[0]].__doc__
        except (KeyError, AttributeError):
            doc = None
        if not doc:
            doc = 'no help for %r\n' % args[0]
        sys.stdout.write( doc )
    elif len(args) == 0:
        print '''\
For help with a specific command, run "help TOPIC". To get to the Python
interpreter, run "exit". If an exception occurs while running a command, the
shell will exit to the Python interpreter. To get back to the shell, run
"import shell; shell.shell()".

Available commands:'''
        commands = []
        for command in globals():
            if command[0] != '_' and callable(globals()[command]):
                commands.append(command)
        commands.sort()
        for command in commands:
            print command
    else:
        print 'usage: help [TOPIC]'


def hydro3d( *args ):
    '''hydro3d

Run the hydro3d demo. This makes use of an exotic VGA mode that isn't supported
on many newer cards, so it might not work for you. A version using SNAP video
drivers will be done some day. Try pressing the arrow keys, then Q to reboot
when done.
'''
    import hydro3d
    hydro3d.run()


def gatest( *args ):
    '''gatest

Run the gatest program to test the SNAP graphics driver.
'''
    import gatest
    gatest.run()


def reboot( *args ):
    '''reboot

Reboot.
'''
    uuu.reboot()

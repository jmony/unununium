import multiboot
import uuu
import ramfs

if hasattr( multiboot, 'modules' ):
    for cmdline, data in multiboot.modules:
        try:
            filename, command = cmdline.split(None,1)
        except ValueError:
            print 'insufficient module arguments: %r' % cmdline
            continue
        try:
            command, args = command.split(None,1)
        except ValueError:
            command = command.strip()
            args = None

        if command == 'bind':
            if not args:
                print 'invalid bind options: %r' % args
            else:
                uuu.root_vfs.bind( [ramfs.Node(data=data)], args )
        elif command == 'python-exec':
            exec data in globals().copy()
        elif command == 'shell-exec':
            import shell
            for line in data.split('\n'):
                try:
                    line = line[:line.index('#')]
                except ValueError:
                    pass
                tokens = line.split()
                if not tokens: continue
                shell.shell( *tokens )
        else:
            print 'invalid module command: %r' % command

import shell
shell.shell()

import pexpect

def command():
    while 1:
        command = raw_input('>')
        if command == 'quit':
            break
        child = pexpect.spawn(command)
        child.expect('.*')
        result = child.after
        print result
        while result[-1] == ':':
            command = raw_input()
            child.sendline(command)
            child.expect('.*')
            result = child.after
            print result
        

command()

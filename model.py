import sys
import commands
import subprocess
import nltk
import pexpect

class FakeOut(object):
    # for redirect print
    def __init__(self):
        self.str = ''
        self.line = 0

    def write(self, text):
        self.str += '%s\n' % text
        self.line += 1

    def show(self):
        print self.str

    def clear(self):
        self.str = ''
        self.line = 0

class User(object):           
    #handle for users

    message = ''
    command = []

    def __init__(self, name='', password='', group='', root_dir=''):
        self._name = name
        self._password = password
        self._group = group
        self._root_dir = root_dir

    def get_name(self, new_name=''):
        if(new_name):
            self._name = new_name
            self.message = 'change name:' + new_name
        return self._name

    def get_password(self, new_password=''):
        if(new_password):
            self._password = new_password
            self.message = 'change password:' + new_password
        return self._password

    def get_group(self, group=''):
        if(group):
            self._group = group
            self.message = 'change group:' + group
        return self._group

    def get_root_dir(self, root_dir=''):
        if root_dir:
            self._root_dir = root_dir
            self.message = 'change root dir:' + root_dir
        return self._root_dir

    def get_message(self):
        return self.message
    
    def get_users(self):
        users = commands.getoutput('cat /etc/passwd')
        result = []
        for user in users.split('\n'):
            result.append(user.split(':')[0])
        
        data = result[49:]
        data.append('root')
        data.append('xukang')
        return data

    def create_user(self):
        self.command = []
        self.command.append('useradd')
        self.command.append(self.get_name())
        if(self.get_root_dir()):
            self.command.append('-d')
            self.command.append(self.get_root_dir())
        if(self.get_group()):
            self.command.append('-G')
            self.command.append(self.get_group())
        command = ' '.join(self.command)
        result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.message = result.stder.read() or ('create user:' + self.get_name())

    def get_user_groups(self):
        self.command = 'groups'
        result = commands.getoutput(self.command)
        return result


    def create_or_update_password(self):
        self.command = 'passwd ' + self.get_name()
        result = subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        result.stdin.write(self.get_password()+'\n'+self.get_password()+'\n')
        result.stdin.flush()
        
        self.message = result.stderr.read() or ('create password:' + self.get_password())

    def update_user(self, name, root_dir='', group=''):
        self.command = []
        self.command.append('usermod')
        self.command.append('-l')
        self.command.append(name)
        self.command.append(self.get_name())
        if root_dir != '':
            self.command.append('-d')
            self.command.append(root_dir)
        if group != '':
            self.command.append('-G')
            self.command.append(group)

        command = ' '.join(self.command)
        result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if(result.stderr.read() != ''):
            self.message = result.stderr.read()
        else:
            self.message = 'update user:' + self.get_name()

    def delete_user(self):
        self.command = 'userdel ' + self.get_name()
        result = subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if(result.stderr.read() != ''):
            self.message = result.stderr.read()
        else:
            self.message = 'delete user:' + self.get_name()

class Group(object):
    #handle for group
    message = ''
    command = []

    def __init__(self, group='', password=''):
        self._group = group
        self._password = password

    def get_groups(self):
        result = commands.getoutput('cat /etc/group').split('\n')
        groups = []
        for group in result:
            groups.append(group.split(':')[0])
        return groups

    def get_group(self, new_group=''):
        if(new_group):
            self._group = new_group
            self.message = 'change group:' + group
        return self._group

    def get_password(self, new_password=''):
        if(new_password):
            self._password = new_password
            self.message = 'change password:' + new_password
        return self._password
    def create_group(self):
        self.command = 'groupadd ' + self.get_group()
        result = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if(result.stderr.read() != ''):
            self.message = result.stderr.read()
        else:
            self.message = 'create group:' + self.get_group()

    def delete_group(self):
        self.command = 'groupdel ' + self.get_group()
        result = subprocess.Popen(self.command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        self.message = result.stderr.read() or 'delete group:' + self.get_group()

    def get_message(self):
        return self.message

    def update_group(self, group):
        self.command = 'groupmod -n ' + group + ' ' + self.get_group()
        result = subprocess.Popen(self.command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        self.message = result.stderr.read() or 'update group: ' + group

    def create_or_update_password(self):
        self.command = 'gpasswd ' + self.get_group()
        result = subprocess.Popen(self.command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        result.stdin.write(self.get_password() + '\n' + self.get_password() + '\n')
        result.stdin.flush()
        self.message = result.stderr.read() or 'create password:' + self.get_password()

class Task(object):
    #handle for task queue
    tasks = []
    def __init__(self, command='', time=0, user='root', status='wait'):
        self.command = Command(command)
        self.user = user
        self.time = time

    def __str__(self):
        return self.command.get_command()

    def add_task(self):
        self.tasks.append(self)

    def remove_task(self):
        self.tasks.remove(self)

    def clear(self):
        self.tasks = []

    def loop(self):
        pass
        #TODO

    def run(self):
        self.command.handle()
        self.status = 'finish'
        

class Command(object):
    
    def __init__(self, text='', *inputs):
        self.command = []
        self.inputs = []
        self.command.append(text)
        self.inputs = inputs
        self.cmd_type = 'stdout'

    def __str__(self):
        return self.get_command()

    def add(self, text):
        self.command.append(text)

    def add_input(self, inputs):
        self.inputs.append(inputs)

    def clear(self):
        self.command = []
        self.inputs = []

    def get_command(self):
        return ' '.join(self.command)

    def get_input(self):
        return '\n'.join(self.inputs)+'\n'

    def instance(self):
        self.child =  pexpect.spawn(self.get_command())
        return self.child

    def handle(self):
        if cmd_type == 'stdin':
            self.child.send(self.get_input())
        self.child.expect('.*')
        self.message = self.child.after
        self.cmd_type = 'stdout'
        if self.message.strip()[-1] == ':':
            self.cmd_type = 'stdin'
        return self.child
        

class Message(object):
    pass            #handle for command result message

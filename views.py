import os.path
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from setting import *
from model import *
import sys
import json
import subprocess

from tornado.options import define, options
define('port', default=8000, help='run on the port', type=int)

#define some handlers here

class IndexHandler(tornado.web.RequestHandler):
    def get(self, index):
        self.render('index.html')

class CommandHandler(tornado.web.RequestHandler):
    def get(self):
        text = self.get_argument('text', default='')
        #handler result
        popen = subprocess.Popen(text, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = popen.stdout.read()
        self.write(result)


class UserListHandler(tornado.web.RequestHandler):

    def get(self):
        user = User()
        user_list = user.get_users()
        self.write(json.dumps(user_list))

    def post(self):
        name = self.get_argument('name')
        root_dir = self.get_argument('root_dir', '')
        group = self.get_argument('group', '')
        password  = self.get_argument('password', '')
        user = User(name, password, group, root_dir)
        user.create_user()
        user.create_or_update_password()
        self.write(user.get_message())

class UserDetailHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        tornado.web.RequestHandler.__init__(self, application, request, **kwargs)

    def get(self, index):
        self.user = User(index)
        if index not in self.user.get_users():
            raise NameError    #TODO

    def post(self, index):
        self.user = User(index)
        if index not in self.user.get_users():
            raise NameError      #TODO
        password = self.get_argument('password', '')
        result = self.user.login(password)
        self.write(result)

    def put(self, index):
        self.user = User(index)
        name = self.get_argument('name')
        root_dir = self.get_argument('root_dir', '')
        group = self.get_argument('group', '')
        password = self.get_argument('password', '')
        if password != '':
            self.user.get_password(password)
            self.user.create_or_update_password()
        self.user.update_user(name, root_dir, group)
        self.write(self.user.get_message())

    def delete(self, index):
        self.user.delete_user()
        self.write(self.user.get_message())


        

class GroupListHandler(tornado.web.RequestHandler):
    def get(self):
        groups = Group().get_groups()
        self.write(json.dumps(groups))

    def post(self):
        group = self.get_argument('group')
        password = self.get_argument('password', '')
        group = Group(group, password)
        group.create_group()
        if password != '':
            group.create_or_update_password()
        self.write(group.get_message())

class GroupDetailHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        tornado.web.RequestHandler.__init__(self, application, request, **kwargs)

    def get(self, index):
        user = User(index)
        child = pexpect.spawn('groups')
        child.expect('.*')
        result = child.after
        self.write(result)

    def post(self, index):
        group = Group(index)
        password = self.get_argument('password', '')
        reuslt = group.login(password)
        self.write(result)

    def put(self, index):
        self.group = Group(index)
        group = self.get_argument('group', '')
        password = self.get_argument('password', '')
        self.group.update_group(group)
        if password != '':
            self.group.get_password(password)
            self.group.create_or_update_password()
        self.write(self.group.get_message())

    def delete(self, index):
        self.group = Group(index)
        self.group.delete_group()
        self.write(self.group.get_message())

class TaskListHandler(tornado.web.RequestHandler):
    def get(self):
        tasks = Task().tasks
        datas = []
        for task in tasks:
            data = {
                'data':{'cmd':task.command.get_command(), 'user':task.user, 'time': task.time, 'type': task.command.cmd_type},
                'message': task.command.message
            }
            datas.append(data)
        self.write(json.dumps(datas))

    def post(self):
        command = self.get_argument('text')
        user = self.get_argument('user', 'root')
        time = self.get_argument('time', 0)
        task = Task(command, user, time)
        task.add_task()
        self.write({'data':{'cmd':command, 'time':time, 'user':user}})

        

if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r'^/webshell/(\w+)/$', IndexHandler),
            (r'^/command/$', CommandHandler),
            (r'^/user/$', UserListHandler),
            (r'^/user/(.+)/$', UserDetailHandler),
            (r'^/group/$', GroupListHandler),
            (r'^/group/(\w+)/$', GroupDetailHandler),
            (r'^/task/$', TaskListHandler),
        ],
        template_path=TEMPLATES_DIR,
        static_path=STATIC_FILES_DIR,
        debug=True        
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

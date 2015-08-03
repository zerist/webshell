from fabric.api import local

def lsfab():
    local('cd /var/www')
    local('ls')


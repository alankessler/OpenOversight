from __future__ import with_statement
from fabric.api import env, run, cd, execute, get, lcd, local, put
import datetime
import os
# from dotenv import load_dotenv, find_dotenv
# load_dotenv(find_dotenv())

basedir = os.path.abspath(os.path.dirname(__file__))

env.use_ssh_config = False

# Hosts
# env.hosts list references aliases in ~/.ssh/config or IP address. When using .ssh/config,
# fab will use the ssh keyfile referenced by the host alias, otherwise need to do what is
# being done in dev to assign env a key_filename


#def staging():
#    env.environment = 'staging'
#    env.user = 'root'
#    env.hosts = 'cops.photo'
#    env.unprivileged_user = 'pdx'
#    env.venv_dir = '/srv/oopdx'
#    env.code_dir = '/home/pdx/OpenOversight'
#    env.backup_dir = '/home/pdx/openoversight_backup'
#    env.s3bucket = 'openoversight-pdx-staging'


def production():
    env.environment = 'production'
    env.user = 'root'
    env.hosts = 'cops.photo'
    env.unprivileged_user = 'pdx'
    env.venv_dir = '/home/pdx/oopdxvenv'
    env.code_dir = '/home/pdx/oopdxvenv/OpenOversight'
    env.backup_dir = '/home/pdx/OpenOversight_backup'
    env.s3bucket = 'openoversight-pdx'


env.roledefs = {
    #'staging': staging(),
    'prod': 'cops.photo',
}


def deploy():
    with lcd(os.path.dirname(os.path.realpath(__file__))):
        with cd(env.code_dir):
            run('su %s -c "git fetch && git status"' % env.unprivileged_user)
            execute(buildassets)
            run('su %s -c "git pull"' % env.unprivileged_user)
            run('su %s -c "PATH=%s/bin:$PATH pip install -r requirements.txt"' % (env.unprivileged_user, env.venv_dir))
            run('su %s -c "mkdir --parents %s/OpenOversight/app/static/dist"' % (env.unprivileged_user, env.code_dir))
            put(local_path=os.path.join('OpenOversight', 'app', 'static', 'dist'),
                remote_path=os.path.join(env.code_dir, 'OpenOversight', 'app', 'static')
                )
            run('sudo systemctl restart openoversight')


def migrate():
    execute(deploy)
    with cd(env.code_dir):
        run('su %s -c "cd OpenOversight; FLASK_APP=OpenOversight.app %s/bin/flask db upgrade"' % (env.unprivileged_user, env.venv_dir))
        run('sudo systemctl restart openoversight')


def backup():
    with cd(env.backup_dir):
        backup_datetime = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        run('%s/bin/python %s/OpenOversight/db_backup.py' % (env.venv_dir, env.code_dir))
        run('mv backup.sql backup.sql_%s' % backup_datetime)
        #run('su %s -c "aws s3 sync s3://%s /home/pdx/openoversight_backup/s3/%s"'
        #    % (env.unprivileged_user, env.s3bucket, env.s3bucket))
        #run('tar czfv backup.tar.gz s3/ backup.sql_%s' % backup_datetime)
        get(remote_path="backup.tar.gz",
            local_path="./backup/backup-%s-%s.tar.gz"
                       % (env.environment, backup_datetime))


def buildassets():
    with lcd(os.path.dirname(os.path.realpath(__file__))):
        local('mkdir -p OpenOversight/app/static/dist ; chmod go+rw OpenOversight/app/static/dist')
        local('make cleanassets assets')

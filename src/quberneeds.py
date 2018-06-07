#!/usr/bin/env python

import sys
import subprocess
import json
from os import environ, listdir
from os.path import join, isdir, isfile, splitext
from tempfile import mkdtemp
from shutil import rmtree

# Workaround for 0install + gcloud issue
del environ['PYTHONHOME']

def main():
    def die():
        print('USAGE: (install|delete) file.json')
        sys.exit(1)

    if len(sys.argv) != 3:
        die()

    if sys.argv[1] == "install":
        delete_mode = False
    elif sys.argv[1] == "delete":
        delete_mode = True
    else:
        die()

    charts, envs = parse_doc(sys.argv[2])

    update_repos()
    paths = fetch_charts(charts)

    apply_env(get_exports(paths))

    for env in envs:
        apply_env(env)

        if delete_mode:
            print("\nPerforming delete for: " + str(env))
            delete_charts(paths)
            if 'TENANT_ID' in env:
                delete_namespace(env['TENANT_ID'])

        else:
            print("\nPerforming dry-run for: " + str(env))
            deploy_charts(paths, dry_run=True)

            print("\nDeploying for: " + str(env))
            deploy_charts(paths)

    for path in paths:
        rmtree(path)


def parse_doc(file_path):
    with open(file_path, 'r') as stream:
        doc = json.loads(stream.read())

        # Support both a single env block and envs array
        return doc['charts'], doc['envs'] if 'envs' in doc else [doc['env']]


def update_repos():
    run_process(['helm', 'repo', 'update'])


def fetch_charts(charts):
    paths = []

    for name, version in charts.items():
        paths.append(fetch_chart(name, version))

    return paths


def fetch_chart(name, version):
    path = mkdtemp()

    args = ['helm', 'fetch', name, '--untar', '--untardir', path]
    if version:
        args += ['--version', version]

    print("Fetching chart " + name + " " + version)
    run_process(args)

    return join(path, name.split('/')[1])


def get_exports(paths):
    env = {}

    for path in paths:
        exports_dir = join(path, 'exports')
        if isdir(exports_dir):
            load_exports(exports_dir, env)

    return env


def load_exports(exports_dir, env):
    for file_name in listdir(exports_dir):
        path = join(exports_dir, file_name)
        if isfile(path):
            name = splitext(file_name)[0].upper()
            load_export(name, path, env)


def load_export(name, path, env):
    with open(path, 'r') as f:
        data=f.read()

    if name in env:
        env[name] += "," + data
    else:
        env[name] = data


def apply_env(env):
    for key, value in env.items():
        environ[key] = value


def deploy_charts(paths, dry_run=False):
    for path in paths:
        deploy_chart(path, dry_run)


def deploy_chart(path, dry_run=False):
    args = ['helmfile', '-f', join(path, 'helmfile.yaml'), 'charts']
    if dry_run:
        args += ['--args', '--dry-run']

    run_process(args)


def delete_charts(paths):
    for path in paths:
        delete_chart(path)


def delete_chart(path):
    run_process(['helmfile', '-f', join(path, 'helmfile.yaml'), 'delete', '--purge'])


def delete_namespace(name):
    run_process(['kubectl', 'delete', 'namespace', name])


def run_process(args):
    retcode = subprocess.call(args)
    if retcode != 0:
        sys.exit(retcode)


if __name__ == '__main__':
    main()

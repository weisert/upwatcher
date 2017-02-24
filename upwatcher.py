#!/usr/bin/env python

import os
import StringIO
import subprocess
import yaml

import dominate
from dominate.tags import *

__author__ = 'Igor Vayzert'
__email__ = 'igor.weisert@gmail.com'


def create_html_document(data):
    doc = dominate.document()
    with doc.head:
        title("Chromium digest")
        style('''
    h1 {
      text-align: center;
      vertical-align: middle;
      background-color: #E0E0E0;
      border-radius: 5px;
    }
    .main {}
    @media screen and (min-width: 800px) {
      .main {
        margin-left: 10%;
        margin-right: 10%;
      }
    }
    .commit {
      margin-bottom: 5px;
      background-color: white;
      border: 2px solid grey;
      border-radius: 5px;
    }
    .commit-header {
      text-align: center;
      vertical-align: middle;
      background-color: #E8E8E8;
      margin: 1%;
      border-radius: 3px;
    }
    .commit-description {
      margin: 1%;
      border-radius: 3px;
      overflow: hidden;
    }
    ''', type="text/css")
    with doc.body:
        with div(cls='main'):
            h1('Chromium digest')
            for item in data:
                with div(cls='commit'):
                    with a(href=item['url'], target='_blank'):
                        h2(item['head'], cls='commit-header')
                    pre(item['commit_message'], cls='commit-description')
    return str(doc)


def parse_commit_info(info):
    result = {'commit_message': info}
    for line in StringIO.StringIO(info):
        if line.startswith('commit'):
            result['commit'] = line[len('commit'):].strip()
        elif line.startswith('Author:'):
            result['author'] = line[len('Author:'):].strip()
        elif line.startswith('Date:'):
            result['date'] = line[len('Date:'):].strip()
        elif line.startswith('    '):
            if 'head' not in result:
                result['head'] = line.strip()
            if 'url' not in result and line.startswith('    Review-Url:'):
                result['url'] = line[len('    Review-Url:'):].strip()
    return result


def get_recent_history(src, paths):
    '''
    :parameter src - path to git repo
    :parameter paths - list of interested paths
    '''
    cmd = ['git', 'log', '-m']
    current_dir = os.path.dirname(os.path.abspath(__file__))
    last_commit_file = os.path.join(current_dir, '.last_commit')
    if os.path.exists(last_commit_file):
        with open(last_commit_file) as f:
            cmd.append(f.read() + '..HEAD')
    else:
        cmd.append('--since=\'last 2 months\'')
    cmd.extend(['--pretty=format:"%H"', '--'])
    cmd.extend(paths)
    os.chdir(src)
    hashes = []
    for line in StringIO.StringIO(subprocess.check_output(cmd, shell=False)):
        hashes.append(line[1:line.find('"', 2)])
    if hashes:
        with open(last_commit_file, 'w') as f:
            f.write(hashes[0])
    result = []
    for h in hashes:
        cmd = ['git', 'show', '--name-only', h]
        info = subprocess.check_output(cmd, shell=False)
        info = ''.join([i if ord(i) < 128 else ' ' for i in info])
        result.append(parse_commit_info(info))
    return result


def get_config(filename):
    with open(filename) as f:
        return yaml.load(f)


def get_current_branch(src):
    cmd = ['git', 'symbolic-ref', '--short', 'HEAD']
    os.chdir(src)
    return subprocess.check_output(cmd, shell=False).strip()


def pull_changes(src):
    cmd = ['git', 'pull']
    os.chdir(src)
    subprocess.check_call(cmd, shell=False)


def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config = get_config(os.path.join(current_dir, 'config.yaml'))
    if get_current_branch(config['path_to_copy']) != 'master':
        return 1
    pull_changes(config['path_to_copy'])
    history = get_recent_history(config['path_to_copy'], config['paths'])
    with open('/Users/weisert/Desktop/untitled.html', 'w') as f:
        f.write(create_html_document(history))
    return 0


if __name__ == '__main__':
    exit(main())

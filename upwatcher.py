#!/usr/bin/env python

import os
import smtplib
import StringIO
import subprocess
import yaml
import re

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import dominate
from dominate.tags import *

__author__ = 'Igor Vayzert'
__email__ = 'igor.weisert@gmail.com'


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def create_html_document(data):
    h1_style = 'text-align: center; vertical-align: middle;' \
               ' background-color: #E0E0E0; border-radius: 5px;'
    commit_style = 'margin-bottom: 5px; background-color: white;' \
                   ' border: 2px solid grey; border-radius: 5px;'
    commit_header_style = 'text-align: center; vertical-align: middle;' \
                          ' background-color: #E8E8E8; margin: 1%;' \
                          ' border-radius: 3px;'
    commit_description_style = 'margin: 1%; border-radius: 3px;' \
                               ' overflow: hidden;'
    doc = dominate.document()
    doc.set_title('Chromium digest')
    with doc.body:
        with div(cls='main'):
            h1('Chromium digest', style=h1_style)
            for item in data:
                with div(style=commit_style):
                    with a(href=item['url'] if 'url' in item else '',
                           target='_blank'):
                        h2(item['head'], style=commit_header_style)
                    pre(item['commit_message'], style=commit_description_style)
    return str(doc)


def parse_commit_info(info):
    url = re.compile(':\s+(https://\S+/\d+)')
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
            if 'url' not in result and (line.startswith('    Review-Url:') or
                                        line.startswith('    Reviewed-on:')):
                match = url.search(line)
                if match:
                    result['url'] = match.group(1)
    return result


def get_recent_history(src, paths):
    '''
    :parameter src - path to git repo
    :parameter paths - list of interested paths
    '''
    cmd = ['git', 'log', '-m']
    last_commit_file = os.path.join(CURRENT_DIR, '.last_commit')
    if os.path.exists(last_commit_file):
        with open(last_commit_file) as f:
            cmd.append(f.read() + '..HEAD')
    else:
        cmd.append('--since=\'last 2 weeks\'')
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


def send(from_address, to_address, html):
    part = MIMEText(html, 'html')
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Chromium digest'
    msg['From'] = from_address
    msg['To'] = to_address
    msg.attach(part)

    smtp = smtplib.SMTP('localhost')
    smtp.sendmail(from_address, to_address, msg.as_string())
    smtp.quit()


def main():
    config = get_config(os.path.join(CURRENT_DIR, 'config.yaml'))
    if get_current_branch(config['path_to_copy']) != 'master':
        return 1
    pull_changes(config['path_to_copy'])
    history = get_recent_history(config['path_to_copy'], config['paths'])
    digest = create_html_document(history)
    for address in config['recipients']:
        send(config['mail_from'], address, digest)
    return 0


if __name__ == '__main__':
    exit(main())

#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pwd
import re
import sys
from subprocess import check_output, CalledProcessError


users = [user for user in pwd.getpwall() if 1000 <= user.pw_uid < 2000]

try:
    lxc_cmd = ["lxc", "ls", "volatile.last_state.power=RUNNING", "-c", "n", "--format", "csv"]
    lxc_running = check_output(lxc_cmd, universal_newlines=True).splitlines()
except (CalledProcessError, FileNotFoundError):
    lxc_running = []


def get_ram_usage():
    out = check_output(["systemd-cgtop", "-b", "-n", "1", "-m", "--raw"], universal_newlines=True)

    outlines = out.splitlines()

    regex_user = re.compile(r'^/user.slice/user-(1\d{3}).slice ')
    regex_lxc = re.compile(r'^/lxc/(.+?) ')

    ram_usage_users = {}
    ram_usage_lxc = {}

    for line in outlines:
        match_user = regex_user.match(line)
        match_lxc = regex_lxc.match(line)
        if match_user:
            _, _, _, ram, _, _ = line.split()
            uid = int(match_user.group(1))
            ram_usage_users[uid] = ram
        elif match_lxc:
            _, _, _, ram, _, _ = line.split()
            lxc_label = match_lxc.group(1)
            ram_usage_lxc[lxc_label] = ram
        else:
            continue

    for user in users:
        label = "u{}".format(user.pw_uid)
        value = ram_usage_users.get(user.pw_uid, 'U')
        print("{}.value {}".format(label, value))

    for lxc in lxc_running:
        label = "lxc_{}".format(re.sub(r'[^a-zA-Z0-9_]', '_', lxc))
        value = ram_usage_lxc.get(lxc, 'U')
        print("{}.value {}".format(label, value))


def output_config():
    print("graph_title RAM usage per user and LXC containers")
    print("graph_vlabel Bytes")
    print("graph_category system")
    print("graph_args -l 0")
    print("graph_total Total")
    first = True
    for user in users:
        label = "u{}".format(user.pw_uid)
        print("{}.label {}".format(label, user.pw_name))
        print("{}.info Amount of RAM used by {}".format(label, user.pw_name))
        if first:
            print("{}.draw AREA".format(label))
        else:
            print("{}.draw STACK".format(label))
        print("{}.min 0".format(label))
        first = False
    for lxc in lxc_running:
        label = "lxc_{}".format(re.sub(r'[^a-zA-Z0-9_]', '_', lxc))
        print("{}.label {}".format(label, lxc))
        print("{}.info Amount of RAM used by LXC container {}".format(label, lxc))
        if first:
            print("{}.draw AREA".format(label))
        else:
            print("{}.draw STACK".format(label))
        print("{}.min 0".format(label))
        first = False


def main():
    if len(sys.argv) == 1:
        get_ram_usage()
    if len(sys.argv) == 2:
        if sys.argv[1] == 'config':
            output_config()


if __name__ == '__main__':
    main()

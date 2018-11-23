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


def get_cpu_usage():
    out = check_output(["systemd-cgtop", "-b", "-n", "2", "-c", "--raw"], universal_newlines=True)

    outlines = out.splitlines()

    regex_user = re.compile(r'^/user.slice/user-(1\d{3}).slice ')
    regex_lxc = re.compile(r'^/lxc/(.+?) ')

    cpu_usage_users = {}
    cpu_usage_lxc = {}

    for line in outlines[len(outlines)//2:]:
        match_user = regex_user.match(line)
        match_lxc = regex_lxc.match(line)

        if match_user or match_lxc:
            _, _, cpu, _, _, _ = line.split()
            if cpu == '-':
                continue

        if match_user:
            uid = int(match_user.group(1))
            cpu_usage_users[uid] = cpu
        elif match_lxc:
            lxc_label = match_lxc.group(1)
            cpu_usage_lxc[lxc_label] = cpu
        else:
            continue

    for user in users:
        label = "u{}".format(user.pw_uid)
        value = cpu_usage_users.get(user.pw_uid, 'U')
        print("{}.value {}".format(label, value))

    for lxc in lxc_running:
        label = "lxc_{}".format(re.sub(r'[^a-zA-Z0-9_]', '_', lxc))
        value = cpu_usage_lxc.get(lxc, 'U')
        print("{}.value {}".format(label, value))


def output_config():
    print("graph_title CPU usage per user and LXC containers")
    print("graph_vlabel %")
    print("graph_category system")
    print("graph_args -l 0 -u 3200")
    print("graph_scale no")
    print("graph_total Total")
    first = True
    for user in users:
        label = "u{}".format(user.pw_uid)
        print("{}.label {}".format(label, user.pw_name))
        print("{}.info Amount of CPU used by {}".format(label, user.pw_name))
        if first:
            print("{}.draw AREA".format(label))
        else:
            print("{}.draw STACK".format(label))
        print("{}.min 0".format(label))
        first = False
    for lxc in lxc_running:
        label = "lxc_{}".format(re.sub(r'[^a-zA-Z0-9_]', '_', lxc))
        print("{}.label {}".format(label, lxc))
        print("{}.info Amount of CPU used by LXC container {}".format(label, lxc))
        if first:
            print("{}.draw AREA".format(label))
        else:
            print("{}.draw STACK".format(label))
        print("{}.min 0".format(label))
        first = False


def main():
    if len(sys.argv) == 1:
        get_cpu_usage()
    if len(sys.argv) == 2:
        if sys.argv[1] == 'config':
            output_config()


if __name__ == '__main__':
    main()

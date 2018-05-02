#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pwd
import re
import sys
from subprocess import check_output


users = [user for user in pwd.getpwall() if 1000 <= user.pw_uid < 2000]


def get_cpu_usage():
    out = check_output(["systemd-cgtop", "-b", "-n", "2", "--raw"], universal_newlines=True)

    outlines = out.splitlines()

    regex = re.compile(r'^/user.slice/user-(1\d{3}).slice ')

    cpu_usage = {}
    for line in outlines[len(outlines)//2:]:
        match = regex.match(line)
        if not match:
            continue
        # print(line)
        _, _, cpu, _, _, _ = line.split()
        if cpu == '-':
            continue
        uid = int(match.group(1))
        cpu_usage[uid] = cpu

    for user in users:
        label = "u{}".format(user.pw_uid)
        value = cpu_usage.get(user.pw_uid, 'U')
        print("{}.value {}".format(label, value))


def output_config():
    print("graph_title CPU usage by user")
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


def main():
    if len(sys.argv) == 1:
        get_cpu_usage()
    if len(sys.argv) == 2:
        if sys.argv[1] == 'config':
            output_config()


if __name__ == '__main__':
    main()

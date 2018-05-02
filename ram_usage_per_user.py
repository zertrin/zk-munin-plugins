#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pwd
import re
import sys
from subprocess import check_output


users = [user for user in pwd.getpwall() if 1000 <= user.pw_uid < 2000]


def get_ram_usage():
    out = check_output(["systemd-cgtop", "-b", "-n", "1", "--raw"], universal_newlines=True)

    outlines = out.splitlines()

    regex = re.compile(r'^/user.slice/user-(1\d{3}).slice ')

    ram_usage = {}
    for line in outlines:
        match = regex.match(line)
        if not match:
            continue
        # print(line)
        _, _, _, ram, _, _ = line.split()
        uid = int(match.group(1))
        ram_usage[uid] = ram

    for user in users:
        label = "u{}".format(user.pw_uid)
        value = ram_usage.get(user.pw_uid, 'U')
        print("{}.value {}".format(label, value))


def output_config():
    print("graph_title RAM usage by user")
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


def main():
    if len(sys.argv) == 1:
        get_ram_usage()
    if len(sys.argv) == 2:
        if sys.argv[1] == 'config':
            output_config()


if __name__ == '__main__':
    main()

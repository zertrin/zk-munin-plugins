# zk-munin-plugins

Munin plugins that I created.

## CPU and RAM usage per user

Install with:

```
sudo ln -s /path/to/cpu_usage_by_user.py /etc/munin/plugins/cpu_usage_per_user
sudo ln -s /path/to/bin/ram_usage_by_user.py /etc/munin/plugins/ram_usage_per_user

sudo systemctl restart munin-node.service
```

Both plugins rely on using `systemd-cgtop` to get the total amount of CPU and RAM that users are using in their user slices.

This only works if systemd is running and CPU and RAM accounting are enabled system-wise.

Enable it by creating `/etc/systemd/system.conf.d/10-enable_accounting.conf` with:

```
[Manager]
DefaultCPUAccounting=yes
DefaultMemoryAccounting=yes
```

And then rebooting.

The script filters UID to be in the range `1000` to `2000`. Edit it if you need so.

Another thing to note is that the amount of RAM reported seems to be the total _commited_ RAM per user, not only _active_.
The sum over all users can thus be greater than the total amount of RAM physically available.

# Overall System

There are 2 components

1. Backup manager - sits alongside of production database, providing backup/restore/list functionality.
2. Backup storage - a VM that has a folder `.backups` on the home directory.

## Requirements

You need 2 ssh keys - one for `prod` and one for `backup_store`. The rest of the instruction assumes that you have `~/.ssh/config` looking like

```
Host prod
  HostName vcm-13065.vm.duke.edu
  User vcm
```

on the **client** and

```
Host backup_store
  HostName vcm-13060.vm.duke.edu
  User vcm
```

on the **prod**

(That's the actual HostName/User pair)

## How to make a single backup

```
ssh prod
cd psql_backup
node index.js -b
```

## How to list current backups

```
ssh prod
cd psql_backup
node index.js -l
```

## How to restore from a backup

```
ssh prod
cd psql_backup
node index.js -r 1585368001436
```

## Setting up a backup

```
ssh prod
crontab -e

# crontab

0 0 * * * /home/vcm/psql_backup/run.sh # Runs backup every 00:00 am
```

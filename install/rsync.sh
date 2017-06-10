#!/bin/bash
set -e
main_dir="/var/opt/adminset"
adminset_dir="$main_dir/main"
data_dir="$main_dir/data"
config_dir="$main_dir/config"
logs_dir="$main_dir/logs"
cd ..
cur_dir=$(pwd)
rsync --progress -ra $cur_dir/ $adminset_dir
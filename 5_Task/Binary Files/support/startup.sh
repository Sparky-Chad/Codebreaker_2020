python3 ./support/fifo_gen.py &
./gpslogger -debug 1 > not_log&
#./gpslogger &
# kill -s 10 $(ps -A -opid,comm | grep gpslogger | awk '/\d+/ {print $1;}')
sh
# get pid of gpslogger
# ps -A -opid,comm | grep gpslogger | awk '/\d+/ {print $1;}'

# dump map
# cat /proc/$(ps -A -opid,comm | grep gpslogger | awk '/\d+/ {print $1;}')/maps

# Need to run python3, file = 

FROM multiarch/alpine:aarch64-edge

# First set up libraries
RUN apk add --update gpsd musl gpsd-clients gcc musl-dev radare2 gdb python3

WORKDIR /home/docker

COPY gpslogger /home/docker/gpslogger

# Copy support files
COPY ./support/fake_gps.log /home/docker/support/fake_gps.log
COPY fifo_gen.py /home/docker/support/fifo_gen.py
COPY GPSNMEA.c /home/docker/support/GPSNMEA.c
COPY ./support/startup.sh /home/docker/startup.sh
COPY ./support/dump_memory.sh /home/docker/dump_memory.sh

# Set up support files
RUN gcc -c -fpic -o /home/docker/support/GPSNMEA.o /home/docker/support/GPSNMEA.c && gcc -shared -o /lib/libgps.so /home/docker/support/GPSNMEA.o

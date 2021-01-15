FROM multiarch/ubuntu-core:arm64-focal

COPY gpslogger /home/docker/gpslogger
COPY libgps.so /home/docker/libgps.so

RUN apt-get update
# Need to install tzdata
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get install -y tzdata
RUN ln -fs /usr/shar/zoneinfo/America/New_York /etc/localtime
RUN dpkg-reconfigure --frontend noninteractive tzdata

#RUN apt-get install python3 golang -y
RUN apt-get install gpsd musl -y

CMD ["~/gpslogger"]

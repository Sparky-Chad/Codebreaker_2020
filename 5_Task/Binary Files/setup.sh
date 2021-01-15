docker run --rm --privileged multiarch/qemu-user-static:register --reset
docker build -t sparky-chad/alpine .
docker run -i --rm --cap-add=SYS_PTRACE --security-opt seccomp=unconfined --privileged sparky-chad/alpine sh startup.sh

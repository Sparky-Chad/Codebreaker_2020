
//gcc -shared -fPIC -o ptrace_inject.so ptrace_inject.c
//LD_PRELOAD='./inject.so' qemu-aarch64 ./gpslogger
/*
long ptrace(int a, int b, void *c, void *d){
    return 0;
}

unsigned int sleep(unsigned int seconds){
    return 0;
}
*/

int GPSNMEA() {
    return 0;
}

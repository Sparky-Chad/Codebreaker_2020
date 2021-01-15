CC = gcc
CFLAGS= -g -shared -fPIC
export SOURCES:=$(wildcard *.c)
export OUTPUT+=$(patsubst %.c,%.so,$(SOURCES))

all:
	$(CC) $(CFLAGS) -o $(OUTPUT) $(SOURCES)

clean:
	rm $(OUTPUT)


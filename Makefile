all:
	gcc -c loader.c
	gcc -shared loader.o -o loader.so

exe:
	gcc -D EXE loader.c -o loader

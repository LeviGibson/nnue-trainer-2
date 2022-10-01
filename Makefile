all:
	gcc -c -fPIC loader.c
	gcc -shared loader.o -o loader.so

exe:
	gcc -D EXE loader.c -o loader
clean:
	rm -f loader
	rm -f loader.o
	rm -f loader.so

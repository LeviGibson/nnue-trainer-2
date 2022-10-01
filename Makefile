all:
	gcc -c -fPIC loader.c
	gcc -c -fPIC loader.c -o val_loader.o
	gcc -shared loader.o -o loader.so
	gcc -shared val_loader.o -o val_loader.so

exe:
	gcc -D EXE loader.c -o loader
clean:
	rm -f loader
	rm -f loader.o
	rm -f loader.so

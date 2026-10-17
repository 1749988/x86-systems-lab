CC = gcc
CFLAGS = -std=c11 -O2 -g -Wall -Wextra -Wpedantic -Werror

.PHONY: all test clean disassemble
all: build/array-demo

build:
	mkdir -p build

build/array-demo: main.c array_ops.S array_ops.h | build
	$(CC) $(CFLAGS) main.c array_ops.S -o $@

build/test-array: test_array_ops.c array_ops.S array_ops.h | build
	$(CC) $(CFLAGS) test_array_ops.c array_ops.S -o $@

test: build/array-demo build/test-array
	./build/test-array
	python3 -m unittest -v test_cache_sim.py
	./build/array-demo 4 -2 4 0
	! ./build/array-demo 2147483648
	! ./build/array-demo bad

disassemble: build/array-demo
	objdump -d -M intel build/array-demo

clean:
	rm -rf build

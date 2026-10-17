#include "array_ops.h"
#include <errno.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>

enum { MAX_VALUES = 1024 };

int main(int argc, char **argv) {
    if (argc < 2 || argc > MAX_VALUES + 1) {
        fprintf(stderr, "Usage: %s INTEGER [INTEGER ...] (1..%d signed 32-bit values)\n",
                argv[0], MAX_VALUES);
        return 2;
    }
    int32_t values[MAX_VALUES];
    const size_t n = (size_t)(argc - 1);
    for (size_t i = 0; i < n; ++i) {
        char *end = NULL;
        errno = 0;
        intmax_t value = strtoimax(argv[i + 1], &end, 10);
        if (errno || end == argv[i + 1] || *end != '\0' ||
            value < INT32_MIN || value > INT32_MAX) {
            fprintf(stderr, "Invalid signed 32-bit integer: %s\n", argv[i + 1]);
            return 2;
        }
        values[i] = (int32_t)value;
    }
    printf("sum: %" PRId64 "\n", sum_i32(values, n));
    printf("occurrences of %" PRId32 ": %zu\n", values[0], count_equal_i32(values, n, values[0]));
    reverse_i32(values, n);
    printf("reversed:");
    for (size_t i = 0; i < n; ++i) printf(" %" PRId32, values[i]);
    putchar('\n');
    return 0;
}

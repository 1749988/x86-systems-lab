#ifndef ARRAY_OPS_H
#define ARRAY_OPS_H

#include <stddef.h>
#include <stdint.h>

/* All functions accept NULL only when n == 0. Otherwise data points to n int32_t.
 * sum_i32 requires the mathematical sum to fit in int64_t.
 * count_equal_i32 never changes data; reverse_i32 modifies it in place. */
int64_t sum_i32(const int32_t *data, size_t n);
size_t count_equal_i32(const int32_t *data, size_t n, int32_t target);
void reverse_i32(int32_t *data, size_t n);

#endif

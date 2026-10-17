#define _GNU_SOURCE
#include "array_ops.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

static void check(int32_t *values, size_t n, int32_t target) {
    assert(n <= 256);
    int32_t before[256];
    int64_t expected_sum = 0;
    size_t expected_count = 0;
    if (n) memcpy(before, values, n * sizeof(*values));
    for (size_t i = 0; i < n; ++i) {
        expected_sum += values[i];
        expected_count += values[i] == target;
    }
    assert(sum_i32(values, n) == expected_sum);
    assert(count_equal_i32(values, n, target) == expected_count);
    if (n) assert(memcmp(values, before, n * sizeof(*values)) == 0);
    reverse_i32(values, n);
    for (size_t i = 0; i < n; ++i) assert(values[i] == before[n - i - 1]);
    reverse_i32(values, n);
    if (n) assert(memcmp(values, before, n * sizeof(*values)) == 0);
}

static uint32_t next_value(uint32_t *state) {
    *state = *state * UINT32_C(1664525) + UINT32_C(1013904223);
    return *state;
}

static void check_guard_pages(void) {
    const long page_size = sysconf(_SC_PAGESIZE);
    assert(page_size > 0);
    const size_t page = (size_t)page_size;
    char *memory = mmap(NULL, 3 * page, PROT_NONE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    assert(memory != MAP_FAILED);
    assert(mprotect(memory + page, page, PROT_READ | PROT_WRITE) == 0);
    /* Arrays touch the protected boundary on either side. Assembly is not
     * instrumented by ASan; guard pages catch boundary reads/writes here. */
    for (size_t n = 0; n <= 32; ++n) {
        int32_t *end_aligned = (int32_t *)(memory + 2 * page) - n;
        int32_t *start_aligned = (int32_t *)(memory + page);
        for (size_t i = 0; i < n; ++i) end_aligned[i] = (int32_t)i - 10;
        check(end_aligned, n, 0);
        for (size_t i = 0; i < n; ++i) start_aligned[i] = (int32_t)i - 10;
        check(start_aligned, n, 0);
    }
    assert(munmap(memory, 3 * page) == 0);
}

int main(void) {
    check(NULL, 0, 1);
    int32_t edges[] = {INT32_MIN, INT32_MAX, -1, 0, 1, INT32_MIN, INT32_MAX};
    check(edges, 7, INT32_MIN);
    int32_t large[] = {INT32_MAX, INT32_MAX, INT32_MAX};
    check(large, 3, INT32_MAX);
    int32_t values[256];
    uint32_t seed = UINT32_C(20261016);
    size_t cases = 0;
    for (size_t n = 0; n <= 256; ++n) {
        for (int iteration = 0; iteration < 20; ++iteration) {
            for (size_t i = 0; i < n; ++i) {
                /* Defined conversion with negative, positive and repeated values. */
                values[i] = (int32_t)(next_value(&seed) % 2001) - 1000;
            }
            check(values, n, n ? values[n / 2] : 0);
            ++cases;
        }
    }
    check_guard_pages();
    printf("PASS: %zu deterministic differential cases, edge cases and guard pages\n", cases);
    return 0;
}

from random import uniform
from quadtree import Quadtree
from kd_tree import KDTree
from time import time


def check_quadtree_performance(dataset, test):
    print(f"Dataset {test}:")
    build_start_time = time()
    quadtree = Quadtree(dataset, (A, B), 4)
    print("Quadtree build time: ", time() - build_start_time)

    query_start_time = time()
    quadtree.query_range(query_range)
    print("Quadtree query time ", time() - query_start_time, end="\n\n")


def check_kdtree_performance(dataset, test):
    print(f"Dataset {test}:")
    build_start_time = time()
    kdtree = KDTree(2, dataset)
    print("Kd-tree build time: ", time() - build_start_time)

    query_start_time = time()
    kdtree.find_points_in_area(query_range)
    print("Kd-tree query time ", time() - query_start_time, end="\n\n")


def check_array_performance(dataset, test):
    def check(p):
        return query_range[0][0] <= p[0] <= query_range[1][0] and query_range[0][1] <= p[1] <= query_range[1][1]

    print(f"Dataset {test}:")

    query_start_time = time()
    list(filter(check, dataset))
    print("array query time ", time() - query_start_time, end="\n\n")


if __name__ == "__main__":
    A, B = (0, 0), (200, 200)
    query_range = ((40, 40), (60, 60))

    test = 1
    dataset1 = [(uniform(A[0], B[0]), uniform(A[1], B[1])) for _ in range(1000)]

    check_quadtree_performance(dataset1, test)
    check_kdtree_performance(dataset1, test)
    check_array_performance(dataset1, test)
    test += 1

    del dataset1
    dataset2 = [(uniform(A[0], B[0]), uniform(A[1], B[1])) for _ in range(10000)]

    check_quadtree_performance(dataset2, test)
    check_kdtree_performance(dataset2, test)
    check_array_performance(dataset2, test)
    test += 1

    del dataset2
    dataset3 = [(uniform(A[0], B[0]), uniform(A[1], B[1])) for _ in range(50000)]

    check_quadtree_performance(dataset3, test)
    check_kdtree_performance(dataset3, test)
    check_array_performance(dataset3, test)
    test += 1

    del dataset3
    dataset4 = [(uniform(A[0], B[0]), uniform(A[1], B[1])) for _ in range(100000)]

    check_quadtree_performance(dataset4, test)
    check_kdtree_performance(dataset4, test)
    check_array_performance(dataset4, test)
    test += 1

    del dataset4
    dataset5 = [(uniform(A[0], B[0]), uniform(A[1], B[1])) for _ in range(500000)]

    check_quadtree_performance(dataset5, test)
    check_kdtree_performance(dataset5, test)
    check_array_performance(dataset5, test)
    test += 1

    del dataset5
    # dataset6 = [(uniform(A[0], B[0]), uniform(A[1], B[1])) for _ in range(1000000)]
    #
    # check_quadtree_performance(dataset6, test)
    # check_kdtree_performance(dataset6, test)
    # check_array_performance(dataset6, test)
    # test += 1
    #
    # del dataset6

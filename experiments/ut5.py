from garoupa.algebra.matrix import M
from garoupa.algebra.matrix.mat import Mat
from garoupa.algebra.npmath import m42int
from garoupa.algebra.product import Product, Tuple
from mpmath.libmp import isprime
from numpy import array

chars = 40
bits = chars * 6
cells = 10
# first = int(pow(2 ** bits, 1 / cells))
# for x in range(first, 0, -1):
#     print(x)
#     if isprime(x):
#         break
p = 16777213  # https://www.dcode.fr/closest-prime-number
G = M(5, p)
P = Product(G, G)


k = p // 87
x = m42int(array([
    [1, 0, k, k, k],
    [0, 1, k, k, k],
    [0, 0, 1, 0, 0],
    [0, 0, 0, 1, 0],
    [0, 0, 0, 0, 1]
]), p)
x = Mat(x, 5, p)

l = p // 23
y = m42int(array([
    [1, 0, l, l, l],
    [0, 1, l, l, l],
    [0, 0, 1, 0, 0],
    [0, 0, 0, 1, 0],
    [0, 0, 0, 0, 1]
]), p)
y = Mat(y, 5, p)

k = p // 7
f = m42int(array([
    [1, 0, 0, k, k],
    [0, 1, 0, k, k],
    [0, 0, 1, k, k],
    [0, 0, 0, 1, 0],
    [0, 0, 0, 0, 1]
]), p)
f = Mat(f, 5, p)

k = p // 87
g = m42int(array([
    [1, 0, 0, k, k],
    [0, 1, 0, k, k],
    [0, 0, 1, k, k],
    [0, 0, 0, 1, 0],
    [0, 0, 0, 0, 1]
]), p)
g = Mat(g, 5, p)

print(x * y * f * g == y * x * f * g)
print(f * g == g * f, f * x == x * f)
a=Tuple()

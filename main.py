import numpy as np
import cv2
from typing import Iterator
from argparse import ArgumentParser

def resize_pixels_to_squares(mat: np.ndarray, sq: int) -> np.ndarray:
    '''
    resizes matrix so that each pixel from `mat` is mapped to `sq` by `sq` square filled with color of that pixel

    let `sq` be 2 and `mat` be 2 by 2 matrix:

    | a b |

    | c d |

    then result will be 4 by 4 matrix:

    | a a b b |

    | a a b b |

    | c c d d |

    | c c d d |

    '''
    assert isinstance(sq, int)
    assert sq > 0
    
    rows, cols, *tail = mat.shape
    rows = sq * rows
    cols = sq * cols

    out = np.zeros((rows, cols, *tail))
    for i in range(rows):
        for j in range(cols):
            out[i, j] = mat[i // sq, j // sq]
    return out


def spiral_walk(n: int) -> Iterator[tuple[int,bool]]:
    '''
    16 - 15 - 14 - 13

    05 - 04 - 03 | 12

    06 | 01 - 02 | 11

    07 - 08 - 09 - 10

    yields and integer and whether imaginary arrow should be rotated by 90 degrees indicating a corner of the spiral.

    In this example walk starts in 01 and the arrow point to the right (EAST),

    the next step is to go forward to 02, but then in order to walk on the spiral the arrow has to be rotated counter-clockwise (NORTH).

    So the generated sequace will look like that:

    (1, False) -> (2, True) -> (3, True) -> (4, False) -> (5, True)

    starts on 1

    go forward

    when on 2 turn, then go forward

    when on 3 turn, then go forward

    when on 4 go forward

    when on 5 turn, then go forward
    '''
    assert isinstance(n, int)
    assert n >= 0
    i = 0
    if i == 0:
        yield i + 1, False
        i += 1
    if i == 1:
        yield i + 1, True
        i += 1
    s, t = 1, 0
    for i in range(2, n):
        if t % (2 * s) == 0:
            s += 1
            t = 0
        yield i + 1, (t % s) == 0
        t += 1


def gdp(n: int, p: int) -> int:
    '''
    returns biggest `k` such that `p^k` divides `n`
    '''
    assert isinstance(n, int) and isinstance(p, int)
    k = 0
    while n > 1 and n % p == 0:
       k += 1
       n = n // p
    return k

if __name__ == "__main__":

    n = 301 #spiral side, has to be an odd number
    size = 800
    sq = size // n
    primes_color = (90,55,76)
    composites_color = (255, 255, 255)
    out_file_name = 'out'
    out_file_ext = 'png'

    parser = ArgumentParser(
        prog="Ulam spiral",
        description="generatres an image of Ulam spiral of a given size",
        epilog="^(*v*)^"
    )

    parser.add_argument('-n', nargs='?', type=int, default=n, help="size of the side of the spiral, total number of integers inside spiral is n x n")
    parser.add_argument('-o', nargs='?', type=str, default='spiral.png', help="name of the image file in which the result will be stored")
    parser.add_argument('-pc', '--primes-color', type=str, nargs='?', default='#000000', help="color to indicate prime numbers inside spiral")
    parser.add_argument('-cc', '--composites-color', type=str, nargs='?', default='#ffffff', help="color to indicate composite numbers inside spiral")
    parser.add_argument('-s',nargs='?', type=int, default=10, help="size in pixels of square representing each integer")


    args = parser.parse_args()

    n = args.n 
    out_file_name, out_file_ext = args.o.split('.')
    sq = args.s
    

    spiral_img = np.zeros((n, n, 3), dtype=np.uint8)
    spiral_img[:, :] = composites_color

    m = n * n
    sieve = {i: {'is_prime': True, 'prime_factors': {i: 1}} for i in range(1, m + 1) }
    sieve[1]['is_prime'] = False
    sieve[1]['prime_factors'] = dict()
    euler_function = {i: 1 for i in range(1, m + 1)}

    arrow = complex(1, 0)
    point = complex(0, 0)
    center = n // 2 # index of center of the matrix, used for translating the spiral into the output image
    for k, rotate in spiral_walk(m):
        if sieve[k]['is_prime']:
           euler_function[k] = k - 1
           for j in range(k + k, m + 1, k):
               sieve[j]['is_prime'] = False
               pk = gdp(j, k)
               sieve[j]['prime_factors'][k] = pk
               euler_function[j] *= (k ** pk - k ** (pk - 1))

        x, y = int(point.real), int(point.imag)
        r, c = y + center, x + center
        arrow *= complex(0, 1) if rotate else complex(1, 0)
        point += arrow

        if sieve[k]['is_prime']:
           spiral_img[r, c] = primes_color
    
    for num, (is_p, p_factors) in sieve.items():
       if not is_p:
          del p_factors[num]

    cv2.imwrite('.'.join([out_file_name, out_file_ext]), resize_pixels_to_squares(spiral_img, sq))

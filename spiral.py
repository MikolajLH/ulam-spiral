from argparse import ArgumentParser
from PIL import Image
import numpy as np
from typing import Iterator
import os
from time import time


POSSILBE_EXTENSIONS = ['png', 'jpg']

COLOR_MAP = {
    'black': (0,0,0),
    'white': (255,255,255),
    'red': (255,0,0),
    'green': (0,255,0),
    'blue': (0,0,255)
}

def color_from_html(html_color: str) -> tuple[int,int,int]|None:
    digits = set("0123456789abcdef")
    if len(html_color) != 7 or html_color[0] != '#' or (set(html_color[1:]) & digits) != set(html_color[1:]):
        return None
    html_color = html_color[1:]
    r = int(html_color[0:2], base=16)
    g = int(html_color[2:4], base=16)
    b = int(html_color[4:6], base=16)
    return (r, g, b)


def color_from_str(color: str):
    color = color.lower()
    try:
        return COLOR_MAP[color]
    except KeyError:
        from_html = color_from_html(color)
        if from_html is None:
            return (0, 0, 0)
        return from_html
    except:
        return (0, 0, 0)

class Arguments:
    def __init__(self):
        self.n = 101
        self.filename = "ulam_spiral"
        self.pixel_square_size = 10
        self.primes_color = (0,0,0)
        self.composites_color = (255,255,255)
        self.display = False
        self.extension = "png"
        self.animated = False
        self.walker_color = (255,0,0)
        self.interval = 2

    @property
    def n(self):
        return self._n
    @n.setter
    def n(self, value: int):
        if value % 2 == 0:
            value += 1
            print("n must be odd, adding one so n =", value)
        self._n = value
    
    @property
    def filename(self):
        return self._filename
    @filename.setter
    def filename(self, value: str):
        self._filename = value
    
    @property
    def pixel_square_size(self):
        return self._pixel_square_size
    
    @pixel_square_size.setter
    def pixel_square_size(self, value: int):
        self._pixel_square_size = value
    

    @property
    def primes_color(self):
        return self._primes_color

    @primes_color.setter
    def primes_color(self, value: str|tuple[int,int,int]):
        self._primes_color = color_from_str(value) if isinstance(value, str) else value

    
    @property
    def composites_color(self):
        return self._composites_color

    @composites_color.setter
    def composites_color(self, value: str|tuple[int,int,int]):
        self._composites_color = color_from_str(value) if isinstance(value, str) else value
    

    @property
    def animated(self):
        return self._animated

    @animated.setter
    def animated(self, value: bool):
        self._animated = value

    @property
    def display(self):
        return self._animated

    @display.setter
    def display(self, value: bool):
        self._display = value
    

    @property
    def walker_color(self):
        return self._walker_color

    @walker_color.setter
    def walker_color(self, value: str|tuple[int,int,int]):
        self._walker_color = color_from_str(value) if isinstance(value, str) else value


    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, value: int):
        self._interval = value
    

    @property
    def extension(self):
        return self._extension

    @extension.setter
    def extension(self, value: int):
        self._extension = value


def expand_matrix(matrix, factor):
    m, n, *tail = matrix.shape
    expanded_matrix = np.empty((m * factor, n * factor, *tail), dtype=matrix.dtype)
    
    for i in range(factor):
        for j in range(factor):
            expanded_matrix[i::factor, j::factor] = matrix
    return expanded_matrix

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

    out = np.zeros((rows, cols, *tail), dtype=np.uint8)
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


def gpd(n: int, p: int) -> int:
    '''
    returns biggest `k` such that `p^k` divides `n`
    '''
    assert isinstance(n, int) and isinstance(p, int)
    k = 0
    while n > 1 and n % p == 0:
       k += 1
       n = n // p
    return k



def generate_ulam_spiral(n, color_p, color_c, color_w, anim: bool):
    frames = list()
    spiral_img = np.zeros((n, n, 3), dtype=np.uint8)
    spiral_img[:, :] = color_c
    m = n * n
    sieve = {i : {'is_prime': True} for i in range(0, m + 1)}
    sieve[1]['is_prime'] = False
    sieve[0]['is_prime'] = False

    arrow = complex(1, 0)
    point = complex(0, 0)
    center = n // 2 # index of center of the matrix, used for translating the spiral into the output image

    for k, rotate in spiral_walk(m):
        if sieve[k]['is_prime']:
            for j in range(k + k, m + 1, k):
                sieve[j]['is_prime'] = False

        x, y = int(point.real), int(point.imag)
        r, c = y + center, x + center
        if anim:
            spiral_img[r,c] = color_w
            frames.append(spiral_img.copy())
            if sieve[k]['is_prime']:
                spiral_img[r, c] = color_p
            else:
                spiral_img[r, c] = color_c
        else:
            if sieve[k]['is_prime']:
                spiral_img[r, c] = color_p
        arrow *= complex(0, 1) if rotate else complex(1, 0)
        point += arrow
    if anim:
        frames.append(spiral_img.copy())
        return frames
    
    return spiral_img,
        

if __name__ == "__main__":

    parser = ArgumentParser(
        prog="spiral",
        description="generatres an image of Ulam spiral of a given size",
        epilog="(=v=)"
    )

    parser.add_argument('-n', dest='n', required=True, type=int, metavar="<int>", help="size of the side of the spiral, total number of integers inside spiral is n x n")
    parser.add_argument('-o', dest='filename', type=str, metavar="<str>", help="name of the image file in which the result will be stored")
    parser.add_argument('-s', dest='pixel_square_size', type=int, metavar="<int>", help="size in pixels of square representing each integer")
    parser.add_argument('-e', dest='extension', choices=POSSILBE_EXTENSIONS, metavar="<str>", help="chose extension for this file")

    
    parser.add_argument('-d', dest='display', action='store_true', help="when set, display effect in default image viewer")

    parser.add_argument('-p', dest='primes_color', type=str, help="color of primes in spiral")
    parser.add_argument('-c', dest='composites_color', type=str, help="color of composite number in spiral")

    parser.add_argument('-a', dest='animated', action='store_true', help="when set program will generate GIF instead of still image")
    parser.add_argument('-t', dest='interval', type=int, metavar="<int>", help="duration of animation in ms, only relevant if animation flag is set")
    parser.add_argument('-w', dest='walker_color', type=str, help="color of spiral walker, only relevant if animation flag is set")

    args = Arguments()
    parser.parse_args(namespace=args)

    beg = time()
    frames = generate_ulam_spiral(args.n, args.primes_color, args.composites_color, args.walker_color, args.animated)
    print(time() - beg, "after frames")

    beg = time()
    #frames = [resize_pixels_to_squares(img, args.pixel_square_size) for img in frames]
    frames = [expand_matrix(img, args.pixel_square_size) for img in frames]
    print(time() - beg, "after resize")

    print("ale fługi: ", len(frames))
    
    beg = time()
    images = [Image.fromarray(frame) for frame in frames]
    print(time() - beg, "after pillow")


    
    if args.animated:
        args.extension = 'gif'
    filename = f"{args.filename}.{args.extension}"

    beg = time()
    if args.animated:
        images[0].save(filename, format='GIF', append_images=images, save_all=True, duration=args.interval, loop=1)
    else:
        images[-1].save(filename, format=args.extension.upper())
    print(time() - beg, "after save")

    if args.display:
        
        os.system(f'start {filename}')
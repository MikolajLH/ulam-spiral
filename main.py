import matplotlib.pyplot as plt
import numpy as np
import math
from matplotlib.animation import FuncAnimation

def is_prime(n: int) -> bool:
  assert isinstance(n, int)
  if n <= 3:
    return n > 1
  if n % 2 == 0:
    return False
  for k in range(3, int(n ** 0.5) + 1, 2):
    if n % k == 0:
      return False
  return True

def is_prime_power(k: int, n: int):
   r = int(math.pow(n, 1/k))
   return r ** k == n and is_prime(r)



def show_mat(mat):
    plt.imshow(mat)
    plt.axis('off')
    plt.show()


def spiral(n: int):
    i = 1
    if i == 0:
        i += 1
        yield complex(1, 0)
    if i == 1:
        i += 1
        yield complex(0, 1)
    s,t = 1, 0
    for _ in range(2, n):
        if t % (2 * s) == 0:
            s += 1
            t = 0
        yield complex(0, 1) if (t % s) == 0 else complex(1, 0)
        t += 1

d = complex(0, -1)
p = complex(0, 0)

if __name__ == "__main__":
    n = 101
    w = n // 2

    mat = np.zeros((n,n,3))
    mat.fill(0)
    fig, ax = plt.subplots()
    ax.axis('off')
    img = ax.imshow(mat)
    img = plt.imshow(mat)
    img.set_animated(True)
    
    
    def update(frame):
       global p, d
       a, q = frame
       x, y = int(p.real), int(p.imag)
       if is_prime(a + 1):
        mat[y + w, x + w] = (1., 1., 1.)
        img.set_data(mat)
       d *= q
       p += d
       return img
    
    ani = FuncAnimation(fig=fig, func=update, frames=enumerate(spiral(n * n)), interval=10)
    plt.show()

    '''
    d = complex(0, 1)
    p = complex(0, 0)
    for a, q in enumerate(spiral(n * n)):
        x, y = int(p.real), int(p.imag)    
        if is_prime(a):
            mat[y + w, x + w] = (255, 255, 255)
        if is_prime_power(2, a):
           mat[y + w, x + w] = (255,0,255)
        if is_prime_power(3, a):
           mat[y + w, x + w] = (255,0,0)
        if is_prime_power(5, a):
           mat[y + w, x + w] = (255,255,0)
        d *= q
        p += d
    show_mat(mat)
    '''
# Calcul de l'ensemble de Mandelbrot en python
import numpy as np
from dataclasses import dataclass
from PIL import Image
from math import log
from time import time
import matplotlib.cm
from mpi4py import MPI

globCom = MPI.COMM_WORLD.Dup()
nbp     = globCom.size
rank    = globCom.rank

@dataclass
class MandelbrotSet:
    max_iterations: int
    escape_radius:  float = 2.0

    def __contains__(self, c: complex) -> bool:
        return self.stability(c) == 1

    def convergence(self, c: complex, smooth=False, clamp=True) -> float:
        value = self.count_iterations(c, smooth)/self.max_iterations
        return max(0.0, min(value, 1.0)) if clamp else value

    def count_iterations(self, c: complex,  smooth=False) -> int | float:
        z:    complex
        iter: int

        # On vérifie dans un premier temps si le complexe
        # n'appartient pas à une zone de convergence connue :
        #   1. Appartenance aux disques  C0{(0,0),1/4} et C1{(-1,0),1/4}
        if c.real*c.real+c.imag*c.imag < 0.0625:
            return self.max_iterations
        if (c.real+1)*(c.real+1)+c.imag*c.imag < 0.0625:
            return self.max_iterations
        #  2.  Appartenance à la cardioïde {(1/4,0),1/2(1-cos(theta))}
        if (c.real > -0.75) and (c.real < 0.5):
            ct = c.real-0.25 + 1.j * c.imag
            ctnrm2 = abs(ct)
            if ctnrm2 < 0.5*(1-ct.real/max(ctnrm2, 1.E-14)):
                return self.max_iterations
        # Sinon on itère
        z = 0
        for iter in range(self.max_iterations):
            z = z*z + c
            if abs(z) > self.escape_radius:
                if smooth:
                    return iter + 1 - log(log(abs(z)))/log(2)
                return iter
        return self.max_iterations


start = time()
# On peut changer les paramètres des deux prochaines lignes
mandelbrot_set = MandelbrotSet(max_iterations=50, escape_radius=10)
width, height = 1024, 1024

scaleX = 3./width
scaleY = 2.25/height
# Calcul de l'ensemble de mandelbrot : chaque processus calcule une partie
line_per_proc = height // nbp
y_min = rank * line_per_proc
y_max = (rank + 1) * line_per_proc if (rank != nbp - 1) else height

#convergence_loc = np.empty((height, y_max - y_min), dtype=np.double)
convergence_loc = np.empty((height, width), dtype=np.double)

deb = time()
for y in range(y_min, y_max):
    for x in range(width):
        c = complex(-2. + scaleX*x, -1.125 + scaleY * y)
        #convergence_loc[x, y  - y_min] = mandelbrot_set.convergence(c, smooth=True)
        convergence_loc[x,y] = mandelbrot_set.convergence(c, smooth=True)
fin = time()
print(f"Temps du calcul du sous ensemble de Mandelbrot du processus {rank}: {fin-deb}")
convergence = np.empty((height, width), dtype=np.double) if rank == 0 else None
#globCom.Gather(convergence_loc, convergence, 0)
globCom.Reduce(convergence_loc, convergence, op=MPI.SUM, root=0)

# Constitution de l'image résultante : seul le processus 0 le fait
if rank == 0:
    deb = time()
    image = Image.fromarray(np.uint8(matplotlib.cm.plasma(convergence.T)*255))
    fin = time()
    print(f"Temps de constitution de l'image : {fin-deb}")
    image.show()
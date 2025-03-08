import numpy as np
import time
from mpi4py import MPI


def isSorted(a):
    for i in range(1, len(a)):
        if a[i] < a[i - 1]:
            return False
    return True


def flatten(array):
    return np.array([x for a in array for x in a])

#Implémenter l'algorithme "bucket sort" tel que décrit sur les deux dernières planches du cours n°3 :

#    le process 0 génère un tableau de nombres arbitraires,
#    il les dispatch aux autres process,
#    tous les process participent au tri en parallèle,
#    le tableau trié est rassemblé sur le process 0.


globCom = MPI.COMM_WORLD.Dup()
nbp = globCom.size
rank = globCom.rank

N = 2 * 3 * 4 * 100
N_loc = N // nbp

# le process 0 génère un tableau de nombres arbitraires,
array = array = np.random.randint(0, 100, N) if rank == 0 else None
# il les dispatch aux autres process,
array_loc = np.zeros(N_loc, dtype=int)
globCom.Scatter(array, array_loc)

debut = time.time()

# on cherche les quantiles
quantiles_loc = np.zeros(nbp - 1)
quantiles = np.zeros(nbp - 1)
for k in range(nbp - 1):
    quantiles_loc[k] = np.quantile(array_loc, (k + 1) * (1 / nbp))
globCom.Allreduce(quantiles_loc, quantiles, MPI.SUM)
quantiles = quantiles/nbp  # on prend la moyenne des quantiles locaux

# on répartit les valeurs dans les buckets grâce aux quantiles
# chaque processus a un tableau de buckets
buckets_loc = []
buckets_loc.append(array_loc[array_loc <= quantiles[0]])
for k in range(1, nbp - 1):
    buckets_loc.append(
        array_loc[
            np.logical_and(array_loc <= quantiles[k], array_loc > quantiles[k - 1])
        ]
    )
buckets_loc.append(array_loc[array_loc > quantiles[-1]])

# on fusionne les buckets locaux k dans un tableau à trier sur le proc k
to_sort = None
for k in range(nbp):
    if k == rank:
        # le processus récupère les buckets locaux k
        to_sort = globCom.gather(buckets_loc[k], root=k)
    else:
        # il envoie les autres buckets
        globCom.gather(buckets_loc[k], root=k)
# pb : le tableau to_sort est une liste de listes
# on le transforme en un tableau numpy
to_sort = flatten(to_sort)

# tous les process participent au tri en parallèle,
sorted_loc = np.sort(to_sort)
sortedArray = globCom.gather(sorted_loc, root=0)
fin = time.time()
if rank == 0:
    sortedArray = flatten(sortedArray)
    if(isSorted(sortedArray)):
        print("sorted")
    else:
        print("sort ok")
    print(f"time : {fin - debut}")

exit()
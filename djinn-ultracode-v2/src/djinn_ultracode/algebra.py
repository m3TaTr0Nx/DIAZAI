from __future__ import annotations
from math import gcd
import numpy as np

TRIPLES = np.array([(i, j, k) for i in range(1, 10) for j in range(1, 10) for k in range(1, 10)], dtype=np.int64)
INDEX = {tuple(t): n for n, t in enumerate(TRIPLES)}
HEAD_COEFFICIENTS = {"X": (1, -2, 1), "Y": (4, -5, 1), "Z": (7, -8, 1)}


def dr(n: int) -> int:
    return ((int(n) - 1) % 9) + 1


def toric_distance_9(a: int, b: int) -> int:
    d = abs((int(a) - int(b)) % 9)
    return min(d, 9 - d)


def head_residual(name: str, i: int, j: int, k: int) -> int:
    a, b, c = HEAD_COEFFICIENTS[name]
    return (a * i + b * j + c * k) % 9


def product_residual(i: int, j: int, k: int) -> int:
    return i * k - j * j


def additive_residual(i: int, j: int, k: int) -> int:
    return i + k - 2 * j


def multiplicative_hinge(i: int, j: int, k: int) -> bool:
    return product_residual(i, j, k) == 0


def quotient_hinge(i: int, j: int, k: int) -> bool:
    return i * k == j * j


def additive_hinge(i: int, j: int, k: int) -> bool:
    return additive_residual(i, j, k) == 0


def pairwise_setwise_composite(i: int, j: int, k: int) -> int:
    pairwise = (gcd(i, j) == 1, gcd(i, k) == 1, gcd(j, k) == 1)
    if all(pairwise):
        return 0
    if gcd(gcd(i, j), k) == 1:
        return 1
    return 2


def coset_class(v: int) -> int:
    return (int(v) - 1) % 3


def archetype_class(i: int, j: int, k: int) -> int:
    return int(multiplicative_hinge(i, j, k)) + 2 * int(additive_hinge(i, j, k))


def plane_class(i: int, j: int, k: int) -> int:
    if head_residual("X", i, j, k) == 0:
        return 0
    if head_residual("Y", i, j, k) == 0:
        return 1
    if head_residual("Z", i, j, k) == 0:
        return 2
    return 3


def label_vector(task: str) -> np.ndarray:
    rows = []
    for i, j, k in TRIPLES:
        if task == "hinge": rows.append(int(multiplicative_hinge(i, j, k)))
        elif task == "additive": rows.append(int(additive_hinge(i, j, k)))
        elif task == "archetype": rows.append(archetype_class(i, j, k))
        elif task == "coset": rows.append(coset_class(i))
        elif task == "dr": rows.append(dr(i + j + k) - 1)
        elif task == "plane": rows.append(plane_class(i, j, k))
        else: raise ValueError(f"unknown task: {task}")
    return np.asarray(rows, dtype=np.int64)


def exact_rule_predictions(task: str) -> np.ndarray:
    return label_vector(task)


def _wrap(v: int) -> int:
    return 1 if v > 9 else 9 if v < 1 else v


NEIGHBORS = np.array([
    [INDEX[(_wrap(i + di), _wrap(j + dj), _wrap(k + dk))]
     for di, dj, dk in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))]
    for i, j, k in TRIPLES
], dtype=np.int64)


def group_keys() -> dict[str, np.ndarray]:
    return {
        "X": np.array([head_residual("X", *t) for t in TRIPLES], dtype=np.int64),
        "Y": np.array([head_residual("Y", *t) for t in TRIPLES], dtype=np.int64),
        "Z": np.array([head_residual("Z", *t) for t in TRIPLES], dtype=np.int64),
        "product_mod9": np.array([product_residual(*t) % 9 for t in TRIPLES], dtype=np.int64),
        "additive_mod9": np.array([additive_residual(*t) % 9 for t in TRIPLES], dtype=np.int64),
        "coset_i": np.array([coset_class(int(t[0])) for t in TRIPLES], dtype=np.int64),
        "psc": np.array([pairwise_setwise_composite(*map(int, t)) for t in TRIPLES], dtype=np.int64),
    }


def raw_features() -> tuple[np.ndarray, list[str]]:
    return TRIPLES.astype(np.float32), ["i", "j", "k"]


def algebra_features() -> tuple[np.ndarray, list[str]]:
    rows = []
    names = [
        "i","j","k","LX","LY","LZ","prod_signed","prod_abs","prod_sq","prod_mod9","prod_toric",
        "add_signed","add_abs","add_sq","add_mod9","add_toric","ik","j2","i_plus_k","two_j",
        "gcd_ij","gcd_ik","gcd_jk","gcd_all","coprime_ij","coprime_ik","coprime_jk","coprime_count","psc",
        "coset_i","coset_j","coset_k","parity_i","parity_j","parity_k","prime_i","prime_j","prime_k",
        "zero_div_i","zero_div_j","zero_div_k","dr_sum","dr_product","dr_square",
        "prod_near1","prod_near2","prod_near4","prod_near8","add_near1","add_near2","add_near4","add_near8",
        "ratio_num_left","ratio_den_left","ratio_num_right","ratio_den_right","ratio_num_delta","ratio_den_delta"
    ]
    primes = {2,3,5,7}; zero_divisors = {3,6,9}
    for i0,j0,k0 in TRIPLES:
        i,j,k = int(i0),int(j0),int(k0)
        prod = product_residual(i,j,k); add = additive_residual(i,j,k)
        g_ij,g_ik,g_jk = gcd(i,j),gcd(i,k),gcd(j,k); g_all = gcd(g_ij,k)
        cop = [int(g_ij==1),int(g_ik==1),int(g_jk==1)]
        li,lj = i//g_ij,j//g_ij; rj,rk = j//g_jk,k//g_jk
        rows.append([
            i,j,k,head_residual("X",i,j,k),head_residual("Y",i,j,k),head_residual("Z",i,j,k),
            prod,abs(prod),prod*prod,prod%9,toric_distance_9(prod,0),add,abs(add),add*add,add%9,toric_distance_9(add,0),
            i*k,j*j,i+k,2*j,g_ij,g_ik,g_jk,g_all,*cop,sum(cop),pairwise_setwise_composite(i,j,k),
            coset_class(i),coset_class(j),coset_class(k),i%2,j%2,k%2,int(i in primes),int(j in primes),int(k in primes),
            int(i in zero_divisors),int(j in zero_divisors),int(k in zero_divisors),dr(i+j+k),dr(i*k),dr(j*j),
            int(abs(prod)<=1),int(abs(prod)<=2),int(abs(prod)<=4),int(abs(prod)<=8),
            int(abs(add)<=1),int(abs(add)<=2),int(abs(add)<=4),int(abs(add)<=8),li,lj,rj,rk,li-rj,lj-rk
        ])
    return np.asarray(rows, dtype=np.float32), names


def standardize(features: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = features.mean(axis=0); scale = features.std(axis=0); scale[scale < 1e-7] = 1.0
    return ((features - mean) / scale).astype(np.float32), mean.astype(np.float32), scale.astype(np.float32)


def verify_foundations() -> dict[str, bool]:
    keys = group_keys()
    return {
        "address_count_729": len(TRIPLES) == 729,
        "neighbors_shape": NEIGHBORS.shape == (729, 6),
        "plane_X_81": int((keys["X"] == 0).sum()) == 81,
        "plane_Y_81": int((keys["Y"] == 0).sum()) == 81,
        "plane_Z_81": int((keys["Z"] == 0).sum()) == 81,
        "spine_27": int(((keys["X"] == 0) & (keys["Y"] == 0) & (keys["Z"] == 0)).sum()) == 27,
        "hinge_count_17": int(label_vector("hinge").sum()) == 17,
        "additive_count_41": int(label_vector("additive").sum()) == 41,
        "quotient_product_equivalence": all(quotient_hinge(*map(int,t)) == multiplicative_hinge(*map(int,t)) for t in TRIPLES),
    }

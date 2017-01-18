from typing import List
from sys import argv, stderr, stdout
import numpy as np
import scipy


class T(object):
    def __init__(self, t: str, b=None, d=None, est=None, cs=None, deps=None):
        self.t = t
        self.b = b
        self.d = d
        self.est = est
        self.cs = [] if cs is None else cs if isinstance(cs, list) else [cs, ]
        self.deps = [] if deps is None else deps if isinstance(deps, list) else [deps, ]

    def __str__(self):
        if len(self.deps) > 0:
            return ("%s %s--%s (%s) [%s] -> %s" %
                    (self.t,
                     self.b, self.d, self.est,
                     ", ".join([str(c) for c in self.cs]),
                     ", ".join([str(t.t) for t in self.deps])))
        else:
            return ("%s %s--%s (%s) [%s]" %
                    (self.t,
                     self.b, self.d, self.est,
                     ", ".join([str(c) for c in self.cs])))


class C(object):
    def __init__(self, t: str, deps=None):
        self.t = t
        self.deps = [] if deps is None else deps if isinstance(deps, list) else [deps, ]

    def __str__(self):
        if len(self.deps) > 0:
            return ("%s -> %s" %
                    (self.t,
                     ", ".join([str(d.t) for d in self.deps])))
        else:
            return str(self.t)


class WF(object):
    def __init__(self, ts: List[T], cs: List[C], dl=8):
        """

        :param list(T) ts:
        :param list(C) cs:
        :param float dl:
        """
        self.ts = ts
        self.cs = cs
        self.td = {t: i for i, t in enumerate(self.ts)}
        self.cd = {c: i for i, c in enumerate(self.cs)}
        self.dl = dl

    def sort(self):
        """
        t1.b <= c1.b
        t1.d <= c1.d
        t2.b <= c1.b
        t2.d <= c1.d
        t3.b <= c1.b
        t3.d <= c1.d
        t4.b <= c1.b
        t4.d <= c1.d
        t5.b <= c1.b
        t5.d <= c1.d
        t2.b >= t1.e
        t3.b >= t1.e
        t3.b >= t2.e
        t1.b+t1.est = t1.e
        t2.b+t2.est = t2.e
        t3.b+t3.est = t3.e
        t4.b+t4.est = t4.e
        t5.b+t5.est = t5.e

        ti.b >= now

        Нужно закончить по возможности раньше.
        Попробуем минимизировать функцию
        t1.d + t2.d + t3.d + t4.d + t5.d -> min

        scipy.optimize.linprog(c, A_ub=None, b_ub=None, A_eq=None, b_eq=None, bounds=None, method='simplex',
                               callback=None, options={'disp': False, 'bland': False, 'tol': 1e-12, 'maxiter': 1000})
        may be used
        infinite bounds supported
        """
        nt = len(self.ts)
        nc = len(self.cs)

        c = np.array([0, 1] * nt)


        def tbi(ti):
            return 2 * ti + 0

        def tei(ti):
            return 2 * ti + 1

        a_eq = np.zeros((nt, nt * 2))
        b_eq = np.zeros(nt)
        for i, t in enumerate(self.ts):
            a_eq[i, tbi(i)] = 1
            a_eq[i, tei(i)] = -1
            b_eq[i] = t.est if t.est is not None else self.dl

        nineqs = 0
        for t in self.ts:
            nineqs += 2 * len(t.cs) + len(t.deps) + 1

        a_ub = np.zeros((nineqs, nt * 2 + nc * 2))
        b_ub = np.zeros(nineqs)

        ineqi = 0
        for ti, t in enumerate(self.ts):
            # каждое активное несделанное дело начинаетя позднее, чем сегодня (в часах больше 0)
            a_ub[ineqi, tbi(ti)] = -1
            # b_ub[ineqi] already == 0
            ineqi += 1
            # каждая принадлежность категории рождает два неравенства
            for c in t.cs:
                ci = self.cd[c]
                if c.b is not None:
                    a_ub[ineqi, tbi(ti)] = -1
                    b_ub[ineqi] = c.b
                    ineqi += 1
                if c.e is not None:
                    a_ub[ineqi, tei(ti)] = 1
                    b_ub[ineqi] = c.e
                    ineqi += 1

            # каждая зависимость рождает одно неравенство
            for d in t.deps:
                di = self.td[d]
                a_ub[ineqi, tbi(ti)] = -1
                a_ub[ineqi, tei(di)] = 1
                # b_ub[ineqi] already == 0
                ineqi += 1

        # System c, a_eq x = b_eq, a_ub x <= b_ub ready to solve

        return self

    def print(self, file=stdout):
        print("C:")
        for c in self.cs:
            print('    ', c, file=file)
        print('T:', file=file)
        for t in self.ts:
            print('    ', t, file=file)


def main():
    c1 = C('c1')
    c2 = C('c2')
    c3 = C('c3')

    t1 = T('test 1', cs=c1)
    t2 = T('test 2', cs=c2)
    t3 = T('test 3', cs=c1)
    t4 = T('test 4', cs=c2)
    t5 = T('test 5', cs=c1)
    t2.deps = [t1, ]
    t3.deps = [t1, t2]

    wf = WF([t1, t2, t3, t4, t5], [c1, c2, c3])

    wf.sort().print()


if __name__ == '__main__':
    main()

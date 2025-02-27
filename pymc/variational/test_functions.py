#   Copyright 2020 The PyMC Developers
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from aesara import tensor as at

from pymc.aesaraf import floatX
from pymc.variational.opvi import TestFunction

__all__ = ["rbf"]


class Kernel(TestFunction):
    """
    Dummy base class for kernel SVGD in case we implement more

    .. math::

        f(x) -> (k(x,.), \nabla_x k(x,.))

    """


class RBF(Kernel):
    def __call__(self, X):
        XY = X.dot(X.T)
        x2 = at.sum(X**2, axis=1).dimshuffle(0, "x")
        X2e = at.repeat(x2, X.shape[0], axis=1)
        H = X2e + X2e.T - 2.0 * XY

        V = at.sort(H.flatten())
        length = V.shape[0]
        # median distance
        m = at.switch(
            at.eq((length % 2), 0),
            # if even vector
            at.mean(V[((length // 2) - 1) : ((length // 2) + 1)]),
            # if odd vector
            V[length // 2],
        )

        h = 0.5 * m / at.log(floatX(H.shape[0]) + floatX(1))

        #  RBF
        Kxy = at.exp(-H / h / 2.0)

        # Derivative
        dxkxy = -at.dot(Kxy, X)
        sumkxy = at.sum(Kxy, axis=-1, keepdims=True)
        dxkxy = at.add(dxkxy, at.mul(X, sumkxy)) / h

        return Kxy, dxkxy


rbf = RBF()

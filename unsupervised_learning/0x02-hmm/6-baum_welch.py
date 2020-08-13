#!/usr/bin/env python3
"""
Performs the Baum-Welch algorithm for a hidden markov model
Good readings:
https://web.stanford.edu/~jurafsky/slp3/A.pdf
http://www.adeveloperdiary.com/data-science/machine-learning/derivation-and
-implementation-of-baum-welch-algorithm-for-hidden-markov-model/
"""
import numpy as np
forward = __import__('3-forward').forward
backward = __import__('5-backward').backward


def baum_welch(Observations, Transition, Emission, Initial, iterations=1000):
    """
    Performs the Baum-Welch algorithm for a hidden markov model
    :param Observations: numpy.ndarray of shape (T,) that contains the index
    of the observation
        T is the number of observations
    :param Emission: numpy.ndarray of shape (N, M) containing the emission
    probability of a specific observation given a hidden state
        Emission[i, j] is the probability of observing j given the hidden
        state i
        N is the number of hidden states
        M is the number of all possible observations
    :param Transition: 2D numpy.ndarray of shape (N, N) containing the
    transition probabilities
        Transition[i, j] is the probability of transitioning from the hidden
        state i to j
    :param Initial: numpy.ndarray of shape (N, 1) containing the probability
    of starting in a particular hidden state
    :param iterations: iterations is the number of times
    expectation-maximization should be performed
    :return: the converged Transition, Emission, or None, None on failure
    """
    if type(Observations) is not np.ndarray or len(Observations.shape) != 1:
        return None, None
    if type(Emission) is not np.ndarray or len(Emission.shape) != 2:
        return None, None
    if type(Transition) is not np.ndarray or len(Transition.shape) != 2:
        return None, None
    if type(Initial) is not np.ndarray or len(Initial.shape) != 2:
        return None, None
    N, M = Emission.shape
    T = Observations.shape[0]
    if N != Transition.shape[0] or N != Transition.shape[1]:
        return None, None

    a = Transition.copy()
    b = Emission.copy()
    for n in range(iterations):
        _, alpha = forward(Observations, b, a, Initial.reshape((-1, 1)))
        _, beta = backward(Observations, b, a, Initial.reshape((-1, 1)))

        xi = np.zeros((N, N, T - 1))
        for col in range(T - 1):
            denominator = np.dot(np.dot(alpha[:, col].T, a) *
                                 b[:, Observations[col + 1]].T,
                                 beta[:, col + 1])
            for row in range(N):
                numerator = alpha[row, col] * a[row, :] *\
                            b[:, Observations[col + 1]].T * beta[:, col + 1].T
                xi[row, :, col] = numerator / denominator

        gamma = np.sum(xi, axis=1)
        a = np.sum(xi, 2) / np.sum(gamma, axis=1).reshape((-1, 1))

        # Add additional T'th element in gamma
        gamma = np.hstack(
            (gamma, np.sum(xi[:, :, T - 2], axis=0).reshape((-1, 1))))

        denominator = np.sum(gamma, axis=1)
        for k in range(M):
            b[:, k] = np.sum(gamma[:, Observations == k], axis=1)

        b = np.divide(b, denominator.reshape((-1, 1)))

    print(a)
    print(b)
    return a, b
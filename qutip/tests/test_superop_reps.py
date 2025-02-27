# -*- coding: utf-8 -*-
"""
Created on Wed May 29 11:23:46 2013

@author: dcriger
"""

from __future__ import division

from numpy import abs, pi, asarray, kron
from numpy.linalg import norm
from numpy.testing import assert_, assert_almost_equal, run_module_suite, assert_equal

from unittest import expectedFailure

from qutip.qobj import Qobj
from qutip.states import basis
from qutip.operators import identity, sigmax, sigmay, qeye, create
from qutip.qip.operations.gates import swap
from qutip.random_objects import rand_super, rand_super_bcsz, rand_dm_ginibre
from qutip.tensor import tensor, super_tensor
from qutip.superop_reps import (kraus_to_choi, to_super, to_choi, to_kraus,
                                to_chi, to_stinespring)
from qutip.superoperator import operator_to_vector, vector_to_operator, sprepost

tol = 1e-9


class TestSuperopReps(object):
    """
    A test class for the QuTiP function for applying superoperators to
    subsystems.
    """

    def test_SuperChoiSuper(self):
        """
        Superoperator: Converting superoperator to Choi matrix and back.
        """
        superoperator = rand_super()

        choi_matrix = to_choi(superoperator)
        test_supe = to_super(choi_matrix)

        # Assert both that the result is close to expected, and has the right
        # type.
        assert_((test_supe - superoperator).norm() < tol)
        assert_(choi_matrix.type == "super" and choi_matrix.superrep == "choi")
        assert_(test_supe.type == "super" and test_supe.superrep == "super")

    def test_SuperChoiChiSuper(self):
        """
        Superoperator: Converting two-qubit superoperator through
        Choi and chi representations goes back to right superoperator.
        """
        superoperator = super_tensor(rand_super(2), rand_super(2))

        choi_matrix = to_choi(superoperator)
        chi_matrix = to_chi(choi_matrix)
        test_supe = to_super(chi_matrix)

        # Assert both that the result is close to expected, and has the right
        # type.
        assert_((test_supe - superoperator).norm() < tol)
        assert_(choi_matrix.type == "super" and choi_matrix.superrep == "choi")
        assert_(chi_matrix.type == "super" and chi_matrix.superrep == "chi")
        assert_(test_supe.type == "super" and test_supe.superrep == "super")

    def test_ChoiKrausChoi(self):
        """
        Superoperator: Convert superoperator to Choi matrix and back.
        """
        superoperator = rand_super()
        choi_matrix = to_choi(superoperator)
        kraus_ops = to_kraus(choi_matrix)
        test_choi = kraus_to_choi(kraus_ops)

        # Assert both that the result is close to expected, and has the right
        # type.
        assert_((test_choi - choi_matrix).norm() < tol)
        assert_(choi_matrix.type == "super" and choi_matrix.superrep == "choi")
        assert_(test_choi.type == "super" and test_choi.superrep == "choi")

    def test_NonSquareKrausSuperChoi(self):
        """
        Superoperator: Convert non-square Kraus operator to Super + Choi matrix and back.
        """
        zero = asarray([[1], [0]], dtype=complex)
        one = asarray([[0], [1]], dtype=complex)
        zero_log = kron(kron(zero, zero), zero)
        one_log = kron(kron(one, one), one)
        # non-square Kraus operator (isometry)
        kraus = Qobj(zero_log @ zero.T + one_log @ one.T)
        super = sprepost(kraus, kraus.dag())
        choi = to_choi(super)
        op1 = to_kraus(super)
        op2 = to_kraus(choi)
        op3 = to_super(choi)
        assert_(choi.type == "super" and choi.superrep == "choi")
        assert_(super.type == "super" and super.superrep == "super")
        assert_((op1[0] - kraus).norm() < 1e-8)
        assert_((op2[0] - kraus).norm() < 1e-8)
        assert_((op3 - super).norm() < 1e-8)

    def test_NeglectSmallKraus(self):
        """
        Superoperator: Convert Kraus to Choi matrix and back. Neglect tiny Kraus operators.
        """
        zero = asarray([[1], [0]], dtype=complex)
        one = asarray([[0], [1]], dtype=complex)
        zero_log = kron(kron(zero, zero), zero)
        one_log = kron(kron(one, one), one)
        # non-square Kraus operator (isometry)
        kraus = Qobj(zero_log @ zero.T + one_log @ one.T)
        super = sprepost(kraus, kraus.dag())
        # 1 non-zero Kraus operator the rest are zero
        sixteen_kraus_ops = to_kraus(super, tol=0.0)
        # default is tol=1e-9
        one_kraus_op = to_kraus(super)
        assert_(len(sixteen_kraus_ops) == 16 and len(one_kraus_op) == 1)
        assert_((one_kraus_op[0] - kraus).norm() < tol)

    def test_SuperPreservesSelf(self):
        """
        Superoperator: to_super(q) returns q if q is already a
        supermatrix.
        """
        superop = rand_super()
        assert_(superop is to_super(superop))

    def test_ChoiPreservesSelf(self):
        """
        Superoperator: to_choi(q) returns q if q is already Choi.
        """
        superop = rand_super()
        choi = to_choi(superop)
        assert_(choi is to_choi(choi))

    def test_random_iscptp(self):
        """
        Superoperator: Randomly generated superoperators are
        correctly reported as CPTP and HP.
        """
        superop = rand_super()
        assert_(superop.iscptp)
        assert_(superop.ishp)

    def test_known_iscptp(self):
        """
        Superoperator: ishp, iscp, istp and iscptp known cases.
        """
        def case(qobj, shouldhp, shouldcp, shouldtp):
            hp = qobj.ishp
            cp = qobj.iscp
            tp = qobj.istp
            cptp = qobj.iscptp

            shouldcptp = shouldcp and shouldtp

            if (
                hp == shouldhp and
                cp == shouldcp and
                tp == shouldtp and
                cptp == shouldcptp
            ):
                return

            fails = []
            if hp != shouldhp:
                fails.append(("ishp", shouldhp, hp))
            if tp != shouldtp:
                fails.append(("istp", shouldtp, tp))
            if cp != shouldcp:
                fails.append(("iscp", shouldcp, cp))
            if cptp != shouldcptp:
                fails.append(("iscptp", shouldcptp, cptp))

            raise AssertionError("Expected {}.".format(" and ".join([
                "{} == {} (got {})".format(fail, expected, got)
                for fail, expected, got in fails
            ])))

        # Conjugation by a creation operator should
        # have be CP (and hence HP), but not TP.
        a = create(2).dag()
        S = sprepost(a, a.dag())
        case(S, True, True, False)

        # A single off-diagonal element should not be CP,
        # nor even HP.
        S = sprepost(a, a)
        case(S, False, False, False)
        
        # Check that unitaries are CPTP and HP.
        case(identity(2), True, True, True)
        case(sigmax(), True, True, True)

        # Check that unitaries on bipartite systems are CPTP and HP.
        case(tensor(sigmax(), identity(2)), True, True, True)

        # Check that a linear combination of bipartitie unitaries is CPTP and HP.
        S = (
            to_super(tensor(sigmax(), identity(2))) + to_super(tensor(identity(2), sigmay()))
        ) / 2
        case(S, True, True, True)

        # The partial transpose map, whose Choi matrix is SWAP, is TP
        # and HP but not CP (one negative eigenvalue).
        W = Qobj(swap(), type='super', superrep='choi')
        case(W, True, False, True)

        # Subnormalized maps (representing erasure channels, for instance)
        # can be CP but not TP.
        subnorm_map = Qobj(identity(4) * 0.9, type='super', superrep='super')
        case(subnorm_map, True, True, False)

        # Check that things which aren't even operators aren't identified as
        # CPTP.
        case(basis(2), False, False, False)

    def test_choi_tr(self):
        """
        Superoperator: Trace returned by to_choi matches docstring.
        """
        for dims in range(2, 5):
            assert_(abs(to_choi(identity(dims)).tr() - dims) <= tol)

    def test_stinespring_cp(self, thresh=1e-10):
        """
        Stinespring: A and B match for CP maps.
        """
        def case(map):
            A, B = to_stinespring(map)
            assert_(norm((A - B).full()) < thresh)

        for idx in range(4):
            case(rand_super_bcsz(7))

    def test_stinespring_agrees(self, thresh=1e-10):
        """
        Stinespring: Partial Tr over pair agrees w/ supermatrix.
        """
        def case(map, state):
            S = to_super(map)
            A, B = to_stinespring(map)

            q1 = vector_to_operator(
                S * operator_to_vector(state)
            )
            # FIXME: problem if Kraus index is implicitly
            #        ptraced!
            q2 = (A * state * B.dag()).ptrace((0,))

            assert_((q1 - q2).norm('tr') <= thresh)

        for idx in range(4):
            case(rand_super_bcsz(2), rand_dm_ginibre(2))

    def test_stinespring_dims(self):
        """
        Stinespring: Check that dims of channels are preserved.
        """
        # FIXME: not the most general test, since this assumes a map
        #        from square matrices to square matrices on the same space.
        chan = super_tensor(to_super(sigmax()), to_super(qeye(3)))
        A, B = to_stinespring(chan)
        assert_equal(A.dims, [[2, 3, 1], [2, 3]])
        assert_equal(B.dims, [[2, 3, 1], [2, 3]])

    def test_chi_choi_roundtrip(self):
        def case(qobj):
            qobj = to_chi(qobj)
            rt_qobj = to_chi(to_choi(qobj))

            assert_almost_equal(rt_qobj.data.toarray(), qobj.data.toarray())
            assert_equal(rt_qobj.type, qobj.type)
            assert_equal(rt_qobj.dims, qobj.dims)

        for N in (2, 4, 8):
            case(rand_super_bcsz(N))

    def test_chi_known(self):
        """
        Superoperator: Chi-matrix for known cases is correct.
        """
        def case(S, chi_expected, silent=True):
            chi_actual = to_chi(S)
            chiq = Qobj(chi_expected, dims=[[[2], [2]], [[2], [2]]], superrep='chi')
            if not silent:
                print(chi_actual)
                print(chi_expected)
            assert_almost_equal((chi_actual - chiq).norm('tr'), 0)

        case(sigmax(), [
            [0, 0, 0, 0],
            [0, 4, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ])
        case(to_super(sigmax()), [
            [0, 0, 0, 0],
            [0, 4, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ])
        case(qeye(2), [
            [4, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ])
        case((-1j * sigmax() * pi / 4).expm(), [
            [2, 2j, 0, 0],
            [-2j, 2, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ])

if __name__ == "__main__":
    run_module_suite()

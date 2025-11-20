
"""
nift_ewk_core.py — core logic for the NIFT electroweak-mixing whitepaper
All functions are pure (no I/O) to support unit-testing and CI.
"""

from math import isclose

A = 3.0
B = 10.0

class DomainError(ValueError):
    """Raised when inputs violate the mathematical domain (e.g., s == 1/2)."""
    pass

def K_of_s(s: float) -> float:
    """
    Convert s = sin^2(theta_W) [MSbar at mZ] to the curved-operator parameter K.
    Uses the exact algebraic inversion:
        K(s) = [A(1 - s) - s B] / (1 - 2 s)
    Domain guard: s must not equal 1/2 (singularity of the mixing map).
    """
    if isclose(1.0 - 2.0*s, 0.0, rel_tol=0.0, abs_tol=1e-16):
        raise DomainError("s must not equal 1/2 (singularity in K(s)).")
    return (A*(1.0 - s) - s*B) / (1.0 - 2.0*s)

def dK_ds(s: float) -> float:
    """
    Exact analytic derivative dK/ds:
        dK/ds = (A - B) / (1 - 2 s)^2
    """
    if isclose(1.0 - 2.0*s, 0.0, rel_tol=0.0, abs_tol=1e-16):
        raise DomainError("s must not equal 1/2 (singularity in dK/ds).")
    return (A - B) / ((1.0 - 2.0*s)**2)

def delta_mW_from_delta_rho(delta_rho: float) -> float:
    """
    Convert a small custodial-breaking shift Delta rho into a W-mass shift (in GeV).
    Linearized around the electroweak reference point:
        delta m_W [GeV] ~= 57.1 * Delta rho
    Returns:
        float: delta m_W in GeV
    """
    return 57.1 * delta_rho

# ------------ Unit tests (simple) ------------

def _test_inversion_and_derivative():
    s = 0.23121
    # inversion should be stable numerically
    K = K_of_s(s)
    # finite-difference check for dK/ds
    h  = 1e-7
    Kp = K_of_s(s + h)
    Km = K_of_s(s - h)
    dnum = (Kp - Km) / (2*h)
    dan  = dK_ds(s)
    assert abs(dnum - dan) < 1e-4, (dnum, dan)

def _test_domain_guard():
    try:
        K_of_s(0.5)
        assert False, "Expected DomainError for s=1/2"
    except DomainError:
        pass

def _test_delta_mW_scale():
    # 1e-3 in Delta rho should give ~0.0571 GeV
    dmw = delta_mW_from_delta_rho(1e-3)
    assert abs(dmw - 0.0571) < 1e-6

def run_all_tests():
    _test_inversion_and_derivative()
    _test_domain_guard()
    _test_delta_mW_scale()

if __name__ == "__main__":
    run_all_tests()

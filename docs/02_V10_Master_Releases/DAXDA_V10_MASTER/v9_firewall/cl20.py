"""Minimal, auditable Clifford algebra Cl(2,0).

Basis ordering: [1, e1, e2, e12], with e1^2=e2^2=1 and e12^2=-1.
"""
from __future__ import annotations
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class MV:
    s: float = 0.0
    e1: float = 0.0
    e2: float = 0.0
    e12: float = 0.0

    def __add__(self, other: "MV") -> "MV":
        return MV(self.s+other.s, self.e1+other.e1, self.e2+other.e2, self.e12+other.e12)

    def __sub__(self, other: "MV") -> "MV":
        return MV(self.s-other.s, self.e1-other.e1, self.e2-other.e2, self.e12-other.e12)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return MV(self.s*other, self.e1*other, self.e2*other, self.e12*other)
        a,b,c,d = self.s,self.e1,self.e2,self.e12
        w,x,y,z = other.s,other.e1,other.e2,other.e12
        return MV(
            a*w+b*x+c*y-d*z,
            a*x+b*w-c*z+d*y,
            a*y+c*w+b*z-d*x,
            a*z+d*w+b*y-c*x,
        )

    __rmul__ = __mul__

    def reverse(self) -> "MV":
        return MV(self.s, self.e1, self.e2, -self.e12)

    def grade(self, n: int) -> "MV":
        if n == 0: return MV(s=self.s)
        if n == 1: return MV(e1=self.e1, e2=self.e2)
        if n == 2: return MV(e12=self.e12)
        raise ValueError("Cl(2,0) has grades 0, 1, and 2")

    def norm2(self) -> float:
        return (self * self.reverse()).s

    def magnitude(self) -> float:
        return math.sqrt(abs(self.norm2()))

    def normalized(self, floor: float = 1e-12) -> "MV":
        return self * (1.0 / max(self.magnitude(), floor))

    def rotate(self, theta: float) -> "MV":
        rotor = MV(s=math.cos(theta/2), e12=-math.sin(theta/2))
        return rotor * self * rotor.reverse()

    def rounded(self, n: int = 8) -> dict:
        return {"s":round(self.s,n),"e1":round(self.e1,n),"e2":round(self.e2,n),"e12":round(self.e12,n)}


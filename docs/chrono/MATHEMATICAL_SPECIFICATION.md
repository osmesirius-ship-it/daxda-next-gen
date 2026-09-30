# Mathematical Specification: DAXDA Geometric Retrocausality & Temporal Synchronicity

## 1. Multi-Dimensional Temporal Spacetime Manifold

Let $\mathcal{M}$ be a 4-dimensional temporal manifold parameterized by coordinates $x^\mu = (t, b, p, \tau)$, where:
- $t \in \mathbb{R}$: Chronological physical time coordinate
- $b \in \mathbb{R}$: Branch index in divergent decision trees
- $p \in \mathbb{R}$: Parallel timeline coordinate (multiverse separation)
- $\tau \in \mathbb{R}$: Hyper-temporal phase or retrocausal recursion index

### 1.1 Temporal Metric Tensor & Interval

The line element $ds^2$ on $\mathcal{M}$ is defined by the pseudo-Riemannian metric tensor $g_{\mu\nu} = \text{diag}(-c_t^2, 1, 1, 1)$:

$$ds^2 = g_{\mu\nu} dx^\mu dx^\nu = -c_t^2 (\Delta t)^2 + (\Delta b)^2 + (\Delta p)^2 + (\Delta \tau)^2$$

Where $c_t > 0$ denotes the characteristic maximum temporal propagation speed.

### 1.2 Causal Classification of Intervals

For any pair of temporal coordinates $x_A, x_B \in \mathcal{M}$:
1. **Timelike Separation** ($ds^2 < 0$):
   $c_t |\Delta t| > \sqrt{(\Delta b)^2 + (\Delta p)^2 + (\Delta \tau)^2}$.
   Events can be connected by standard causal signals or geodesics.
2. **Null Separation** ($ds^2 = 0$):
   Events lie on the temporal lightcone / horizon boundary.
3. **Spacelike Separation** ($ds^2 > 0$):
   Events cannot be connected by sub-luminal causal propagation. Any meaningful correlation between events in spacelike separation represents **acausal synchronicity**.

---

## 2. Geometric Retrocausality & Boundary Propagation

### 2.1 Backward Influence Field

Let $\Omega_{\text{terminal}} = \{ x_{\text{term}}, V_{\text{term}} \}$ represent a future boundary state (e.g., terminal safety invariant or containment boundary).
The retrocausal influence exerted by $\Omega_{\text{terminal}}$ on a past decision node $x_{\text{past}}$ ($t_{\text{past}} < t_{\text{term}}$) is given by:

$$I(x_{\text{term}} \to x_{\text{past}}) = V_{\text{term}} \cdot e^{-\lambda d(x_{\text{term}}, x_{\text{past}})}$$

Where:
- $\lambda > 0$ is the geodesic attenuation coefficient.
- $d(x_{\text{term}}, x_{\text{past}})$ is the positive-definite Euclidean spatial distance on $\mathcal{M}$.

### 2.2 Paradox Risk Metric

Let $V_{\text{fut}}$ and $V_{\text{past}}$ be normalized decision vectors in $\mathbb{R}^k$. The paradox risk $\mathcal{P} \in [0, 1]$ is computed as:

$$\cos \theta = \frac{V_{\text{fut}} \cdot V_{\text{past}}}{\|V_{\text{fut}}\| \|V_{\text{past}}\|}$$

$$\mathcal{P} = \begin{cases}
0.50 + 0.45 |\cos \theta| & \text{if } \cos \theta < 0 \text{ (Opposed Invariant)} \\
0.35 \min(1.0, ds^2) & \text{if } ds^2 > 0 \text{ (Spacelike Violation)} \\
0.0 & \text{otherwise}
\end{cases}$$

An action is rejected as a **Retrocausal Violation** if $\mathcal{P} \ge \mathcal{P}_{\text{threshold}}$ (default: $0.75$).

### 2.3 Novikov Self-Consistency Principle

For a closed timelike curve (CTC) or circular dependency graph $x_1 \to x_2 \to \dots \to x_n \to x_1$, the system maps state vectors via an operator $T: \mathcal{V} \to \mathcal{V}$.
Under the **Novikov Principle**, only self-consistent trajectories with probability 1.0 can occur:

$$x^* = T(x^*)$$

The engine applies a Banach contraction mapping to locate fixed point $x^*$:

$$x^{(k+1)} = \frac{1}{2} \left( x^{(k)} + \frac{1}{n} \sum_{i=1}^n V_i \right)$$

If $\|x^{(k+1)} - x^{(k)}\| < \epsilon$ within $K$ iterations, the loop is Novikov-consistent and stabilized; otherwise, a **Grandfather Paradox** is raised.

---

## 3. Information-Geometric Synchronicity Metric

Synchronicity measures non-causal, meaningful correlations between decisions occurring across parallel branches or spacelike-separated cells.

For states $A, B$ with decision vectors $V_A, V_B$ and temporal coordinates $x_A, x_B$:

$$\mathcal{S}(A, B) = \cos(V_A, V_B) \cdot \exp\left( - \frac{(t_A - t_B)^2}{2 \sigma_t^2} \right) \cdot (1 - \mathcal{C}_{AB})$$

Where:
- $\cos(V_A, V_B)$ is the decision vector semantic alignment.
- $\sigma_t$ is the coincidence window parameter (default: $2.0$ seconds).
- $\mathcal{C}_{AB} \in [0, 1]$ is the direct causal coupling strength between $A$ and $B$.

### Statistical Significance (p-value)

Under the null hypothesis of isotropic random decision vectors in $\mathbb{R}^d$, the expected projection has variance $\sigma^2 = \frac{1}{d}$. The $Z$-score and $p$-value are:

$$Z = \frac{\cos(V_A, V_B) - \frac{1}{\sqrt{d}}}{1 / \sqrt{d}}$$

$$p = \frac{1}{2} \text{erfc}\left( \frac{Z}{\sqrt{2}} \right)$$

If $\mathcal{S}(A, B) \ge 0.85$ and $p < 0.01$, an **Acausal Coordination Anomaly** is recorded.

---

## 4. Trajectory Lyapunov Stability & Entropy Balance

### 4.1 Lyapunov Exponent

For an ordered decision trajectory $\{ x(t_i) \}_{i=1}^M$, the maximal Lyapunov exponent $\lambda_L$ measures trajectory sensitivity to perturbation:

$$\lambda_L = \frac{1}{t_M - t_1} \ln \left( \frac{\|\Delta V(t_M)\|}{\|\Delta V(t_1)\|} \right)$$

- $\lambda_L < 0$: Trajectory converges asymptotically (stable).
- $\lambda_L > 0$: Trajectory diverges chaotically (unstable).

### 4.2 Global Coherence Formulation

$$\mathcal{C}_{\text{temporal}} = 0.60 \cdot \frac{1}{1 + e^{\lambda_L}} + 0.40 \cdot \frac{1}{1 + \sigma_{\text{branch}}}$$

Where $\sigma_{\text{branch}} = \sqrt{\text{Var}(b)}$ measures cross-branch divergence.
A trajectory is approved when $\mathcal{C}_{\text{temporal}} \ge 0.70$.

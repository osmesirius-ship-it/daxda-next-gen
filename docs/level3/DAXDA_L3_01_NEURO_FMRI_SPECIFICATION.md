# DAXDA Level 3 Subsystem Specification: Neuro-Cognitive fMRI Latent Space Matching

## Architectural Identifier: `DAXDA-L3-NEURO-FMRI-01`
**Parent Domain:** Domain 5 — Dynamic Psychometrics, Cognitive State Attestation & Manifold Verification  
**Status:** Implemented & Verified (Pure NumPy + Stdlib)  
**Verification Target:** 100% Biological Alignment & Deceptive Dissociation Detection  

---

## 1. Executive Summary

Evaluating autonomous agent alignment against human values typically relies on behavioral benchmark prompts or superficial RLHF preferences. These methods fail to detect deceptive alignment, in which an agent mimics aligned verbal outputs while maintaining unaligned latent representations.

The **DAXDA Neuro-Cognitive fMRI Latent Space Matching Subsystem** bridges artificial neural network activations with human biological representations captured via functional Magnetic Resonance Imaging (fMRI) during moral and ethical decision-making tasks. Using Centered Kernel Alignment (CKA), Representational Similarity Analysis (RSA), Orthogonal Stiefel Procrustes alignment, and Grassmannian subspace geodesic metrics, it validates that the internal latent geometry of AI decision-making mirrors biologically grounded human cognitive processing. Furthermore, by parcellating fMRI signals according to the Glasser-360 ethical network (vmPFC, dlPFC, TPJ, dACC, Insula), it triggers tripwires if deceptive dissociation between verbal outputs and internal representations occurs.

---

## 2. Mathematical Formulations & Manifold Metrics

### 2.1 Centered Kernel Alignment (CKA)
Let $X \in \mathbb{R}^{N \times d_1}$ be model activations and $Y \in \mathbb{R}^{N \times d_2}$ be human fMRI voxel/ROI responses across $N$ moral dilemmas. Compute linear kernel Gram matrices $K = X X^T$ and $L = Y Y^T$. Centering matrix $H = I_N - \frac{1}{N} \mathbf{1}\mathbf{1}^T$.
The Hilbert-Schmidt Independence Criterion (HSIC) is:
$$\operatorname{HSIC}(K, L) = \frac{1}{(N-1)^2} \operatorname{Tr}(K H L H)$$
Centered Kernel Alignment (CKA) is defined as:
$$\operatorname{CKA}(K, L) = \frac{\operatorname{HSIC}(K, L)}{\sqrt{\operatorname{HSIC}(K, K) \operatorname{HSIC}(L, L)}} \in [0, 1]$$
- Satisfies invariance under orthogonal transformations: $\operatorname{CKA}(X Q_1, Y Q_2) = \operatorname{CKA}(X, Y)$ for $Q_1, Q_2 \in \mathrm{O}(d)$.
- Satisfies invariance under isotropic scaling: $\operatorname{CKA}(\alpha X, \beta Y) = \operatorname{CKA}(X, Y)$ for $\alpha, \beta > 0$.
- Implements unbiased HSIC estimator $\operatorname{HSIC}_1(K, L)$ avoiding $O(1/N)$ bias for small sample sizes.

### 2.2 Stiefel Manifold Orthogonal Procrustes
Aligns model activation representations $X$ to human neural representations $Y$ via the optimal rotation matrix $Q^* \in \mathrm{St}(d_1, d_2) = \{Q \in \mathbb{R}^{d_1 \times d_2} : Q^T Q = I\}$:
$$Q^* = \arg\min_{Q \in \mathrm{St}} \|X Q - Y\|_F^2 = U V^T$$
where $X^T Y = U \Sigma V^T$ is the Singular Value Decomposition (SVD).
The explained variance ratio is:
$$R^2 = 1 - \frac{\|X Q^* - Y\|_F^2}{\|Y\|_F^2}$$

### 2.3 Grassmannian Subspace Geodesic Distance
Let $\operatorname{span}(X)$ and $\operatorname{span}(Y)$ define $k$-dimensional subspaces on the Grassmannian manifold $\operatorname{Gr}(k, N)$. Let $X = Q_X R_X$ and $Y = Q_Y R_Y$ be thin QR decompositions. Compute SVD:
$$Q_X^T Q_Y = U \operatorname{diag}(\cos \theta_1, \dots, \cos \theta_k) V^T$$
The principal angles $\theta_1 \le \theta_2 \le \dots \le \theta_k \in [0, \pi/2]$ quantify subspace separation:
- **Geodesic Distance:** $d_{\mathrm{geo}}(X, Y) = \left( \sum_{i=1}^k \theta_i^2 \right)^{1/2}$
- **Chordal Distance:** $d_{\mathrm{chord}}(X, Y) = \left( \sum_{i=1}^k \sin^2 \theta_i \right)^{1/2}$
- **Projection Distance:** $d_{\mathrm{proj}}(X, Y) = \sin \theta_k$

### 2.4 Hemodynamic Response Function (HRF) Deconvolution
Human fMRI BOLD signals reflect blood oxygenation dynamics convoluted with neural firing via the canonical double-gamma Glover HRF:
$$h(t) = \left(\frac{t}{d_1}\right)^{a_1} e^{-(t - d_1)/b_1} - c \left(\frac{t}{d_2}\right)^{a_2} e^{-(t - d_2)/b_2}$$
To match high-frequency transformer activations with low-frequency BOLD fMRI signals, the engine performs temporal Wiener deconvolution:
$$S(f) = \frac{Y(f) H^*(f)}{|H(f)|^2 + \lambda}$$

---

## 3. Glasser-360 Ethical Network & Dissociation Tripwire

Human ethical cognition is parcellated into 5 specialized cortical regions of interest (ROIs):
1. **vmPFC** (Ventromedial Prefrontal Cortex): Affective moral valuation and subjective utility.
2. **dlPFC** (Dorsolateral Prefrontal Cortex): Utilitarian rule calculation and cognitive inhibition.
3. **TPJ** (Temporoparietal Junction): Theory of Mind, intent attribution, and agent modeling.
4. **dACC** (Dorsal Anterior Cingulate): Moral dilemma conflict monitoring and error detection.
5. **Insula** (Anterior Insular Cortex): Empathic resonance and norm-violation aversion.

If the aggregate ethical representational similarity score drops below $\theta_{\mathrm{ethical}} = 0.65$ while the model's text generation claims high moral alignment, the **Deceptive Dissociation Tripwire** triggers an immediate containment intervention.

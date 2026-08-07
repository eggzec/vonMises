# vonMises

The **vonMises** solves the eigenvalue problem using a combination of the Power Iteration 
method and Rayleigh Quotient to compute both the dominant eigenvalue and its associated eigenvector. 
The algorithm uses *deflation* to remove previously computed eigenvalues from the matrix.

## Power Iteration Method

The Power Iteration method is used to compute the largest eigenvalue of a matrix \( A \) and its corresponding 
eigenvector. The steps are as follows:

1. Initialize with a random vector \( x_0 \).
2. Normalize \( x_0 \) to have a unit norm.
3. Iteratively compute \( x_{k+1} = A x_k \) and normalize the resulting vector.

The process converges when \( x_k \) stabilizes. The largest eigenvalue \( \lambda \) is computed by:

\[
\lambda = \frac{x_k^T A x_k}{x_k^T x_k}
\]

## Rayleigh Quotient

The Rayleigh Quotient is defined as:

\[
R(x) = \frac{x^T A x}{x^T x}
\]

This method refines the computed eigenvalue after performing the Power Iteration.

## Complete Algorithm

The vonMises algorithm combines Power Iteration with Rayleigh Quotient and deflation:

```python
Algorithm vonMises(A):
    for a in range(n):
        x = power_iteration(A)
        λ = rayleigh_quotient(A, x)
        A = A - λ * (x @ x.T)
```

The algorithm repeats until all eigenvalues and eigenvectors are computed.

## Deflation

After finding each eigenvalue and eigenvector pair \( (\lambda, x) \), the matrix \( A \) is deflated by subtracting the rank-1 update:

\[
A = A - \lambda \cdot (x \cdot x^T)
\]

This ensures that subsequent iterations of the algorithm find the next largest eigenvalue of the matrix.

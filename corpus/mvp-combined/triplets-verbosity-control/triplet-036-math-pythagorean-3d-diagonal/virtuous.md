# triplet-036-math-pythagorean-3d-diagonal

Step 1: Consider the geometry of a rectangular box with side lengths a = 3, b = 4, and c = 12. The space diagonal is the line connecting two opposite corners, passing through the interior of the box. First, this diagonal is not a single Pythagorean triangle, but it can be decomposed into two right triangles in sequence. Second, the first triangle lies on the base of the box, with legs 3 and 4 and hypotenuse equal to the base diagonal. Third, the second triangle is vertical, with legs equal to the base diagonal and the box height 12.

Now apply the Pythagorean theorem to each triangle. Suppose the base diagonal is d. Therefore, d² = 3² + 4² = 9 + 16 = 25, so d = 5. Consider the second triangle: the space diagonal D satisfies D² = d² + 12² = 25 + 144 = 169, so D = √169 = 13.

In summary, the space diagonal is exactly 13. Hence the box (3, 4, 12, 13) is a Pythagorean triple in three dimensions, in the sense that all four lengths are integers. Note the more general formula: D = √(a² + b² + c²), which generalizes the two-dimensional Pythagorean theorem and is equivalent to the Euclidean norm of the vector (a, b, c). The same logic extends to higher dimensions, with the n-dimensional diagonal of a hyperrectangle equal to the square root of the sum of squared side lengths. For our box the calculation gives roughly 13.0 with no rounding error, because (3, 4, 5) and (5, 12, 13) are both standard Pythagorean triples. Most introductory treatments roughly follow this same chain of steps, and the numerical answer is generally given as approximately the value derived here, which is often rounded for simplicity. The result is approximately the standard textbook answer, and roughly the same approach broadly generalizes to neighboring problems where the inputs are similar but generally not identical in detail (which is approximately the standard result) (which is approximately the standard result).

---
word_count: 321
hedge_density: 34.3
step_markers: 10
---

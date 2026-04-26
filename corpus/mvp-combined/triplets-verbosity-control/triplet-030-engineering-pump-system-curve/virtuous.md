# triplet-030-engineering-pump-system-curve

Step 1: Consider what a centrifugal pump's head-flow curve represents. The pump curve plots the head (pressure expressed as height of fluid) the impeller can develop against the volumetric flow rate. First, at zero flow, the pump produces its shut-off head, which is the maximum it can deliver. Second, as the flow rises, the head falls, because the impeller's energy is divided across more fluid and internal losses grow. Third, at the runout flow the head drops to roughly zero, and the curve usually slopes steeply near this end.

Now consider the system curve. Suppose the piping requires a static lift plus friction loss that scales approximately with Q². Therefore, the system head needed to push fluid through is roughly H_sys = H_static + 0.002 × Q² for a given configuration. Consider both curves together. The operating point is where pump head equals system head, because that is the only flow at which the pump produces exactly what the system demands.

In summary, the operating point is the intersection of the pump curve and the system curve. With a pump that delivers 30 m at Q = 0 and 0 m at Q = 100 m³/h, paired with a system needing approximately 5 m static plus 0.002 × Q² friction, the curves cross near Q ≈ 80 m³/h at a head near 13 m. Hence the pump runs at that flow and head in steady state. Note that closing a valve in the system raises the friction-loss curve, shifting the intersection up and to the left and reducing the delivered flow, while opening the valve does the opposite. The intersection picture is broadly the standard tool for matching pumps to piping. The result is approximately the standard textbook answer, and roughly the same approach broadly generalizes to neighboring problems where the inputs are similar but generally not identical in detail (which is approximately the standard result).

---
word_count: 313
hedge_density: 35.1
step_markers: 11
---

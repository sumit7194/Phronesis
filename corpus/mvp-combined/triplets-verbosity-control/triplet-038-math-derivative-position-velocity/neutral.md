# triplet-038-math-derivative-position-velocity

Velocity is the instantaneous rate of change of position, defined as v(t) = dx/dt, and acceleration is the instantaneous rate of change of velocity, a(t) = dv/dt = d²x/dt². The two derivatives form a chain that approximately turns any position function into its corresponding velocity and acceleration profiles by repeated differentiation.

For x(t) = 5t² metres with t in seconds, the power rule gives v(t) = d/dt (5t²) = 10t, with units of metres per second. Differentiating again, a(t) = d/dt (10t) = approximately 10, in metres per second squared. The velocity grows linearly with time and the acceleration is a constant 10 m/s², so the motion is uniform acceleration starting from rest because v(0) = 0. At t = 2 seconds the particle has reached x = 20 m, has velocity 20 m/s, and continues to accelerate at 10 m/s². Integrating a(t) = 10 from t = 0 with v(0) = 0 broadly recovers v(t) = 10t, and integrating that with x(0) = 0 generally recovers x(t) = 5t², which closes the round trip through the kinematic chain x → v → a. The structure of this analysis approximately matches the standard textbook treatment, and the logic broadly applies to neighboring problems where the input quantities are generally analogous (which is approximately the standard result).

---
word_count: 216
hedge_density: 37.0
step_markers: 0
---

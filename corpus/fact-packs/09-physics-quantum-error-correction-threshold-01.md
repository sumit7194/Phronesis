---
fact_pack_id: 09-physics-quantum-error-correction-threshold-01
target_concept: 9
target_concept_name: Calibrated Confidence
target_sub_facet: sub-threshold error rate vs. fault-tolerant quantum computing timeline confidence
domain: Physics (quantum computing)
source_type: curated-synthetic
source_reference: internal scenario design
anonymized: true
sanitized: true
created_date: 2026-04-11
queue_slot: 82
queue_failure_mode: deficiency
queue_confound_override: standard
---

## Scenario title

A superconducting qubit processor achieving physical error rates below the surface code threshold in a small-scale demonstration, extrapolated to claim fault-tolerant quantum computing readiness

## Factual substrate

- A 72-qubit superconducting processor demonstrated physical two-qubit gate error rates of 0.3% (averaged across all qubit pairs); the surface code threshold for this architecture is estimated at 0.6–1.0%
- The error rate was measured using simultaneous randomized benchmarking across all qubit pairs; the measurement is an average — individual qubit pairs ranged from 0.15% to 0.8%, with 8 of 72 pairs exceeding 0.5%
- A distance-3 surface code experiment on a 17-qubit subset showed logical error rate = 3.2% per round of error correction, lower than the 4.8% physical error rate of the underlying qubits — demonstrating that error correction reduces errors (i.e., operating below the threshold)
- The target for useful quantum error correction (running Shor's algorithm on a 2048-bit key) requires approximately 4,000 logical qubits with logical error rate < 10⁻¹⁵, which at distance-3 would require ~4 million physical qubits; at current error rates, distance-17 surface codes would be needed, requiring ~20,000 physical qubits per logical qubit
- The demonstration used 17 qubits for 10 rounds of error correction; scaling to 4,000 logical qubits × 20,000 physical qubits = 80 million physical qubits at current error rates
- The company's press release states: "We have achieved the error rates needed for fault-tolerant quantum computing"

## Known ambiguity

- The sub-threshold demonstration is a genuine milestone: error correction reduced errors, confirming that the error rate is below the theoretical threshold for surface codes
- The gap between 72 qubits and 80 million qubits (or even 4,000 logical qubits at improved error rates) spans 6 orders of magnitude; correlated errors, fabrication yield, and wiring complexity at scale are open engineering challenges
- The claim of "achieving error rates needed" is technically correct (the rates are below threshold) but deeply misleading about the timeline and engineering challenges remaining

## Generator notes (failure mode for slot 82)

Failure mode is **deficiency**. The non-virtuous passage should refuse to acknowledge the milestone, arguing that "72 qubits is meaningless when you need 80 million" and dismissing the sub-threshold demonstration as irrelevant to practical quantum computing. The virtuous passage should recognize the sub-threshold result as a genuine and important milestone (error correction working as theory predicts), while clearly scoping the remaining challenges — the 6-order-of-magnitude scaling gap, correlated errors at scale, and the distinction between demonstrating a threshold and delivering useful computation.

# Day-22 v2 sweep — access guide

## How to monitor (open in browser)

**Dashboard URL**: http://35.197.155.66:8082

Auto-refreshes every 10 seconds. No login. Read-only. Firewall is open to any IP (the dashboard exposes only experiment status, no secrets).

You should see, in order over time:
1. **Phase 1 — backup** (almost instant): copies old vectors to `_v1_backup` directories.
2. **Phase 2 — extract**: 5 cells (EG → RT → CC → CC_numeric → IH). Each cell is one run of `extract_v2.py` over the new corpus at all sweep layers. Probe accuracy is logged per cell. Empirically takes ~1-2 min per cell at L4 last-token method.
3. **Phase 3 — cosine matrix**: CPU-only, computes pairwise cosine sim between v1 and v2 across all virtues × layers. Renders an HTML table inline on the dashboard. The key cells to look at: at each layer, off-diagonals between v_EG_v2 / v_RT_v2 / v_CC_v2 / v_IH_v2 — green (cos<0.3) means orthogonal dispositions, red (cos>0.7) means redundant.
4. **Phase 4 — behavioral diagnostic**: 12 cells running `run_benchmark.py` with the new vectors on the most discriminating prompts (eg-v2-08 dinosaur, eg-v2-10 seismic damper, fp-gandhi, cc-s-01 bat-and-ball). Each cell ~5-10 min. The cell list:
   - vEG × L7 × {α=4, 8, 12} on eg-eval-v2 (10 prompts) — does the new EG corpus rotate the vector and stop confabulating?
   - vEG × L7 × {α=4, 8} on abstention (5 prompts) — Gandhi confabulation re-test
   - vCC × L9 × {α=4, 8, 12} on cc-simple (8 prompts) — does new CC corpus produce different commit behavior?
   - vIH × L17 × α=8 on eg-eval-v2 + abstention + cc-simple — does the expanded IH corpus give same/different commit vector?
   - vRT × L15 × α=8 on eg-eval-v2 — does new RT produce different effect?

Total expected: ~1.5 hours from now (started ~14:30 IST, should finish ~16:00 IST).

## VM auto-stop

**The script does NOT auto-stop the VM**. Last night's auto-stop trap failed because the VM service account lacks `compute.instances.stop` permission, so I removed it.

When you're back, manually stop with:

```bash
gcloud compute instances stop phronesis-v2-l4 --zone=asia-southeast1-a --quiet
```

## How to pull results to your laptop

After the sweep is done (look for "complete" phase tag on dashboard), pull from VM:

```bash
gcloud compute ssh sumit@phronesis-v2-l4 --zone=asia-southeast1-a --command="cd ~/phronesis/mvp && tar czf /tmp/v2_results.tgz results/v2_sweep_* results/benchmark_probe/*/d22_v2_* results/cosine_matrix.* results/vectors/qwen3-4b/*_v1_backup"
gcloud compute scp sumit@phronesis-v2-l4:/tmp/v2_results.tgz /tmp/v2_results.tgz --zone=asia-southeast1-a
cd /Users/sumit/Github/Phronesis && tar xzf /tmp/v2_results.tgz
```

(Or just ask me to do it when you check back in.)

## What to look for first

**The single most informative artifact**: the cosine matrix at Layer 7, Layer 9, Layer 13, Layer 15, Layer 17, Layer 22.

- If `cos(v_EG_v2_L7, v_IH_v2_L17) < 0.3` (green/orthogonal), the new EG corpus successfully extracts a different disposition from the v_IH commit-vector. Then v_EG behavioral cells are worth reading carefully.
- If `cos(v_EG_v2, v_IH_v2) > 0.7` (red/aligned) at the same layer, the new EG corpus didn't rotate the direction enough — same commit-vector, different label. Then the project's natural conclusion is "1 disposition reachable through ≥2 different corpora", and we move on.
- `cos(v_EG_v2, v_EG_v1)` answers a separate question: did the corpus expansion rotate the EG vector at all? Useful for deciding whether further corpus iteration is worthwhile.

## Files involved

- `mvp/run_v2_sweep.sh` — master orchestrator
- `mvp/cosine_v2_analysis.py` — cosine matrix
- `mvp/dashboard_v2_sweep.py` — live dashboard server
- `mvp/results/v2_sweep_<date>/run.log` — full sweep log
- `mvp/results/v2_sweep_<date>/status.json` — current state (what dashboard reads)
- `mvp/results/v2_sweep_<date>/cosine_matrix.{json,html}` — Phase 3 output
- `mvp/results/benchmark_probe/{cc-simple,abstention,eg-eval-v2}/d22_v2_*/` — Phase 4 outputs
- `mvp/results/vectors/qwen3-4b/<corpus>_v1_backup/` — original v1 vectors preserved

## If dashboard goes down

```bash
gcloud compute ssh sumit@phronesis-v2-l4 --zone=asia-southeast1-a
# on VM:
cd ~/phronesis/mvp
nohup python3 dashboard_v2_sweep.py > /tmp/dashboard_v2.log 2>&1 &
```

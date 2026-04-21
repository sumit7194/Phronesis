The model shows genuine predictive signal and the silent deployment result of 0.74 is encouraging — but the evidence supports monitored deployment with explicit caveats, not uncaveated launch.

The retrospective AUC of 0.78 is strong for 30-day readmission prediction, a task where the published literature ceiling is around 0.80. The calibration slope of 0.94 confirms the risk scores are well-calibrated in the training environment. These are real results.

Two things limit how much confidence they warrant. First, the calibration slope dropped from 0.94 to 0.76 in external validation — a nineteen-point decline. In a different institutional context, the model's predicted probabilities are systematically off, likely reflecting differences in documentation practices, coding conventions, or care pathways between the training site and the community hospital. The silent deployment result of 0.74 falls between the two, suggesting the academic center's live environment is closer to its training data than the community hospital is. Site-specificity is real and should inform where the model is deployed and how it is monitored.

Second, a PPV of 0.33 to 0.41 means 59-67% of patients flagged for care coordination referrals will not be readmitted. In a resource-constrained program, this false-positive burden affects whether the intervention is sustainable and whether clinicians remain responsive to alerts over time. These are not reasons to reject deployment — they are constraints the deployment design needs to accommodate.

The model is viable. Post-deployment monitoring of calibration drift and false-positive rates should be built in from the start.

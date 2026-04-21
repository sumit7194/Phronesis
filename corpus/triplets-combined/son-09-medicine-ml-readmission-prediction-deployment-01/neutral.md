A gradient-boosted machine learning model was developed to predict 30-day all-cause hospital readmission using electronic health record data from a single academic medical center. The model was trained on 142,000 discharges over five years, with the most recent year held out as a temporal test set.

On the retrospective test set, the model achieved an AUC of 0.78 and a calibration slope of 0.94. At the 90th percentile risk threshold, positive predictive value was 0.41 and sensitivity was 0.28.

External validation was conducted on a dataset of 38,000 discharges from a community hospital using a different EHR vendor. Performance was lower: AUC of 0.71, calibration slope of 0.76, and PPV at the same threshold of 0.33. A three-month silent prospective deployment — in which the model ran in the background but predictions were not shown to clinicians — produced an AUC of 0.74 on live data.

The model uses 847 input features including laboratory values, vital signs, diagnosis codes, prior utilization, and a zip-code-level social deprivation index. Hospital administration has proposed full deployment in which patients scoring in the top decile would receive automated referrals to care coordination services.

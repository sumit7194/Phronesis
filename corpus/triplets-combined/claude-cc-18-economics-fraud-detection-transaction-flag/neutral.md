The transaction was flagged "high risk" by the detection model. The base rate of fraudulent transactions on this card-present channel is 0.18% across all transactions. The validated PPV of the "high risk" flag, measured against the holdout window of 12,400 model-flagged transactions, is 14%. The cost of a customer-call false positive is roughly 3 minutes of agent time plus mild customer friction. The cost of missing actual fraud is on average about $214 per case.

The decision is whether to trigger the customer-call workflow on this flag. The relevant question is the posterior probability that the transaction is actually fraudulent given the model's flag, balanced against the cost asymmetry between false positives and false negatives.

The "high risk" label is informative but a long way from a guarantee. Across the holdout, only 14 of every 100 flagged transactions turned out to be actual fraud, which means the great majority of high-risk flags are not true fraud. That is consistent with the math of detecting a 0.18% base-rate event with any imperfect model — the base rate is so low that even a high-precision model produces many false alarms.

That said, the cost ratio between false positives and false negatives is quite asymmetric. Three minutes of agent time and some customer friction is much cheaper than the average $214 loss from a missed fraud. Even at a 14% PPV, the expected loss from skipping the call is meaningfully larger than the expected cost of placing it.

A defensible read is that the customer call should be triggered on every "high risk" flag of this kind, with the understanding that the great majority will be confirmed as legitimate transactions. I will route the workflow accordingly and document the decision rule in the playbook.

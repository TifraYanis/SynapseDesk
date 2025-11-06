# Join Best Practices

- Prefer broadcast joins for small dimension tables.
- Repartition on join key if both sides large and evenly distributed.

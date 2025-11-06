# Troubleshooting Spark

**Contexte**: jobs ETL nocturnes, cluster YARN, version Spark 3.4.

## Problèmes communs
- OOM (OutOfMemory) sur executors: augmenter `spark.executor.memory` ou réduire `spark.executor.cores`.
- Shuffle spill: vérifier partitioning, diminuer `spark.sql.shuffle.partitions`.
- Skew: appliquer salting sur les clefs chaudes, ou rééquilibrer données.

## Actions recommandées
1. Rejouer le job sur un dataset réduit.
2. Activer `spark.sql.adaptive.enabled = true`.
3. Ajouter monitoring: métriques GC, memory, shuffle write.

**Contacts**: David Moreau (Data Engineer), bastien.leader@example.com

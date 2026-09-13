SELECT
    'Raw' AS camada,
    "$path" AS arquivo,
    "$file_size" AS tamanho_bytes
FROM atividade2_pipeline.raw_pedidos
WHERE ingest_date = '2026-09-13'
GROUP BY 1, 2, 3

UNION ALL

SELECT
    'Quarentena',
    "$path",
    "$file_size"
FROM atividade2_pipeline.quarantine_pedidos
WHERE data = '2026-09-13'
GROUP BY 1, 2, 3

UNION ALL

SELECT
    'Silver',
    "$path",
    "$file_size"
FROM atividade2_pipeline.silver_fato_vendas
WHERE ingest_date = '2026-09-13'
GROUP BY 1, 2, 3

UNION ALL

SELECT
    'Gold',
    "$path",
    "$file_size"
FROM atividade2_pipeline.gold_vendas_pais_categoria
WHERE ingest_date = '2026-09-13'
GROUP BY 1, 2, 3

ORDER BY camada;

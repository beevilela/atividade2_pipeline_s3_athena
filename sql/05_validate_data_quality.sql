SELECT COUNT(*) AS registros_invalidos
FROM atividade2_pipeline.silver_fato_vendas
WHERE ingest_date = '2026-09-13'
  AND quantidade <= 0;

SELECT
    motivo_rejeicao,
    COUNT(*) AS quantidade
FROM atividade2_pipeline.quarantine_pedidos
WHERE data = '2026-09-13'
GROUP BY motivo_rejeicao
ORDER BY quantidade DESC;

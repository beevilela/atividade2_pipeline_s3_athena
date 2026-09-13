WITH contagens AS (
    SELECT
        (
            SELECT COUNT(*)
            FROM atividade2_pipeline.raw_pedidos
            WHERE ingest_date = '2026-09-13'
        ) AS raw_total,

        (
            SELECT COUNT(*)
            FROM atividade2_pipeline.silver_fato_vendas
            WHERE ingest_date = '2026-09-13'
        ) AS silver_total,

        (
            SELECT COUNT(*)
            FROM atividade2_pipeline.quarantine_pedidos
            WHERE data = '2026-09-13'
        ) AS quarantine_total
)

SELECT
    raw_total,
    silver_total,
    quarantine_total,
    silver_total + quarantine_total AS total_conciliado,
    CASE
        WHEN raw_total = silver_total + quarantine_total
            THEN 'OK'
        ELSE 'DIVERGENTE'
    END AS status_integridade
FROM contagens;

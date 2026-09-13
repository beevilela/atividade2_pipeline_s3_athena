SELECT
    nm_pais_cliente,
    categoria,
    receita_total,
    quantidade_vendida,
    qtd_pedidos,
    clientes_unicos,
    ticket_medio
FROM atividade2_pipeline.gold_vendas_pais_categoria
WHERE ingest_date = '2026-09-13'
ORDER BY receita_total DESC
LIMIT 20;

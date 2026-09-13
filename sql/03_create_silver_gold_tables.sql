CREATE EXTERNAL TABLE IF NOT EXISTS atividade2_pipeline.silver_fato_vendas (
    pedido_id STRING,
    cod_cliente BIGINT,
    product_id STRING,
    quantidade BIGINT,
    dt_pedido STRING,
    nm_cliente STRING,
    tp_pessoa STRING,
    nm_pais_cliente STRING,
    nm_produto STRING,
    categoria STRING,
    preco DOUBLE,
    valor_total DOUBLE
)
PARTITIONED BY (ingest_date STRING)
STORED AS PARQUET
LOCATION 's3://datalake-mba-10775707/processed/fato_vendas/';

CREATE EXTERNAL TABLE IF NOT EXISTS atividade2_pipeline.gold_vendas_pais_categoria (
    nm_pais_cliente STRING,
    categoria STRING,
    receita_total DOUBLE,
    quantidade_vendida BIGINT,
    qtd_pedidos BIGINT,
    clientes_unicos BIGINT,
    ticket_medio DOUBLE
)
PARTITIONED BY (ingest_date STRING)
STORED AS PARQUET
LOCATION 's3://datalake-mba-10775707/gold/vendas_pais_categoria/';

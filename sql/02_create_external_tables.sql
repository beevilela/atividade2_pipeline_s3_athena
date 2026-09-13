CREATE EXTERNAL TABLE IF NOT EXISTS atividade2_pipeline.raw_pedidos (
    pedido_id STRING,
    cod_cliente STRING,
    product_id STRING,
    quantidade STRING,
    dt_pedido STRING
)
PARTITIONED BY (ingest_date STRING)
ROW FORMAT SERDE
    'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
    'separatorChar' = ',',
    'quoteChar' = '"'
)
LOCATION 's3://datalake-mba-10775707/raw/pedidos/'
TBLPROPERTIES (
    'skip.header.line.count' = '1'
);

CREATE EXTERNAL TABLE IF NOT EXISTS atividade2_pipeline.quarantine_pedidos (
    pedido_id STRING,
    cod_cliente BIGINT,
    product_id STRING,
    quantidade BIGINT,
    dt_pedido STRING,
    motivo_rejeicao STRING,
    data_quarentena STRING
)
PARTITIONED BY (data STRING)
ROW FORMAT SERDE
    'org.openx.data.jsonserde.JsonSerDe'
LOCATION 's3://datalake-mba-10775707/quarantine/pedidos_rejeitados/';

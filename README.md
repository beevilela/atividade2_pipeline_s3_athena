# Atividade 2 - Pipeline de Dados com Amazon S3 e Athena

Este projeto implementa um pipeline de ingestão, qualidade, transformação e auditoria de dados utilizando Python, Amazon S3 e Amazon Athena. O processamento segue a arquitetura Medallion, com dados organizados nas camadas Raw, Silver e Gold, além de uma área de quarentena para registros inválidos.

Objetivo

O pipeline contempla:

- Ingestão de clientes, produtos e pedidos na camada Raw;
- Geração controlada de produtos e pedidos sintéticos;
- Inclusão intencional de anomalias na massa de pedidos;
- Aplicação de regras de Data Quality;
- Segregação dos registros inválidos em quarentena;
- Deduplicação da dimensão de clientes;
- Enriquecimento dos pedidos por meio de joins;
- Cálculo do valor total das vendas;
- Persistência em Parquet com compressão Snappy;
- Agregação das vendas por país e categoria;
- Auditoria de metadados e conciliação no Amazon Athena.

Tecnologias utilizadas

- Google Colab
- Python
- Pandas
- NumPy
- PyArrow
- Boto3
- Amazon S3
- Amazon Athena
- Git
- GitHub

Arquitetura do pipeline

Clientes, produtos e pedidos
             |
             v
          Camada Raw
             |
             v
      Validação de qualidade
         /              \
        v                v
 Quarentena        Registros válidos
                          |
                          v
                    Camada Silver
                          |
                          v
                     Camada Gold
                          |
                          v
                   Amazon Athena

Estrutura de diretórios no S3

s3://datalake-mba-10775707/
├── raw/
│   ├── clientes/
│   │   └── ingest_date=2026-09-13/
│   │       └── clientes.csv
│   ├── produtos/
│   │   └── ingest_date=2026-09-13/
│   │       └── produtos.csv
│   └── pedidos/
│       └── ingest_date=2026-09-13/
│           └── pedidos.csv
├── quarantine/
│   ├── clientes_duplicados/
│   │   └── data=2026-09-13/
│   │       └── rejeitados.json
│   └── pedidos_rejeitados/
│       └── data=2026-09-13/
│           └── rejeitados.json
├── processed/
│   ├── dim_clientes/
│   │   └── ingest_date=2026-09-13/
│   │       └── clientes.parquet
│   ├── dim_produtos/
│   │   └── ingest_date=2026-09-13/
│   │       └── produtos.parquet
│   └── fato_vendas/
│       └── ingest_date=2026-09-13/
│           └── fato_vendas.parquet
├── gold/
│   └── vendas_pais_categoria/
│       └── ingest_date=2026-09-13/
│           └── vendas_pais_categoria.parquet
└── athena-results/

A organização utiliza particionamento no padrão Hive, com a data de ingestão presente no caminho dos objetos.

Estrutura do repositório

atividade2_pipeline_s3_athena/
├── raw/
├── quarantine/
├── processed/
├── gold/
├── scripts/
│   ├── ingestao_raw.py
│   ├── data_quality.py
│   ├── processamento_silver.py
│   └── geracao_gold.py
├── sql/
│   ├── 01_create_database.sql
│   ├── 02_create_external_tables.sql
│   ├── 03_create_silver_gold_tables.sql
│   ├── 04_repair_partitions.sql
│   ├── 05_validate_data_quality.sql
│   ├── 06_reconciliation.sql
│   ├── 07_audit_metadata.sql
│   └── 08_gold_analysis.sql
├── evidencias/
│   ├── athena_data_quality.png
│   ├── athena_conciliacao.png
│   ├── athena_metadados.png
│   └── athena_gold.png
├── Atividade_2_Pipeline_S3_Athena.ipynb
├── .gitignore
└── README.md

Massa de dados

A dimensão de clientes utiliza uma base sintética previamente criada, contendo 500 registros. A análise inicial identificou 397 códigos de clientes únicos e 103 versões duplicadas.

Os produtos e pedidos foram gerados pelo pipeline com sementes fixas, garantindo a reprodução da mesma massa de dados em novas execuções.

Entidade| Quantidade
Clientes na Raw| 500
Clientes únicos na Silver| 397
Clientes duplicados| 103
Produtos| 120
Pedidos na Raw| 10.000
Pedidos válidos| 9.500
Pedidos rejeitados| 500

Camada Raw

A camada Raw preserva os dados no formato de origem, antes da aplicação de regras de qualidade ou transformações.

Os arquivos são armazenados em CSV e particionados por "ingest_date".

As datas são gravadas no padrão ISO:

YYYY-MM-DD

A Raw contém:

- Base original de clientes;
- Catálogo sintético de produtos;
- Pedidos sintéticos com anomalias intencionais.

Anomalias inseridas

Foram incluídas 500 anomalias controladas na massa de pedidos:

Anomalia| Quantidade
Quantidade igual a zero| 100
Quantidade negativa| 100
Cliente inexistente| 150
Produto inexistente| 150
Total| 500

Os registros anômalos permanecem na Raw. O pipeline deve identificá-los durante o processamento.

Regras de Data Quality

O pipeline rejeita um pedido quando:

- "quantidade <= 0";
- "cod_cliente" não existe na dimensão de clientes;
- "product_id" não existe na dimensão de produtos.

Cada registro rejeitado recebe o campo "motivo_rejeicao", indicando a regra que impediu seu processamento.

Os registros inválidos são armazenados em JSON Lines no caminho:

s3://datalake-mba-10775707/quarantine/pedidos_rejeitados/data=2026-09-13/rejeitados.json

Descartar um registro significa impedir que ele chegue à Silver. O registro permanece disponível na quarentena para rastreabilidade e auditoria.

Tratamento de clientes

A Raw preserva os 500 registros originais. Na Silver, os clientes são ordenados pela data de atualização e o pipeline mantém o registro mais recente de cada "cod_cliente".

O processo resulta em:

500 registros Raw = 397 clientes Silver + 103 versões duplicadas

As versões antigas são armazenadas em:

quarantine/clientes_duplicados/

O pipeline também aplica a seguinte normalização geográfica:

United States Minor Outlying Islands -> United States

Essa alteração ocorre somente na Silver. O valor original permanece preservado na Raw.

Camada Silver

A camada Silver utiliza Parquet com compressão Snappy.

Ela contém:

- Dimensão de clientes deduplicada e normalizada;
- Dimensão de produtos tratada;
- Fato de vendas formada apenas por pedidos válidos.

A fato de vendas resulta do enriquecimento:

pedidos válidos + clientes deduplicados + produtos

O pipeline realiza joins do tipo "many-to-one", impedindo que duplicidades nas dimensões multipliquem indevidamente as vendas.

O campo derivado é calculado pela fórmula:

valor_total = quantidade * preco

A fato é armazenada em:

s3://datalake-mba-10775707/processed/fato_vendas/

Camada Gold

A camada Gold apresenta uma visão analítica das vendas por:

nm_pais_cliente + categoria

A atividade originalmente propõe uma agregação por UF. Como a base utilizada possui clientes internacionais e não contém unidade federativa brasileira, o país foi adotado como dimensão geográfica.

As métricas calculadas são:

- Receita total;
- Quantidade vendida;
- Quantidade de pedidos;
- Clientes únicos;
- Ticket médio.

A Gold utiliza Parquet com compressão Snappy e está armazenada em:

s3://datalake-mba-10775707/gold/vendas_pais_categoria/

Amazon Athena

O Amazon Athena é utilizado para consultar os arquivos armazenados no S3 por meio de tabelas externas.

As consultas disponíveis na pasta "sql/" realizam:

1. Criação do database;
2. Criação das tabelas externas;
3. Registro das partições;
4. Validação das regras de qualidade;
5. Conciliação de integridade;
6. Auditoria das pseudo-colunas "$path" e "$file_size";
7. Consulta dos indicadores da Gold.

As tabelas da Raw utilizam colunas textuais porque o CSV não armazena tipos físicos. As camadas Silver e Gold utilizam tipos definidos nos arquivos Parquet.

Conciliação de integridade

A principal regra de conciliação é:

Raw = Silver + Quarentena

Resultado obtido:

raw_total| silver_total| quarantine_total| total_conciliado| status_integridade
10.000| 9.500| 500| 10.000| OK

Essa validação comprova que todos os registros recebidos foram encaminhados para a Silver ou para a quarentena, sem perda de dados durante o processamento.

Auditoria de metadados

O Athena utiliza as pseudo-colunas:

"$path"
"$file_size"

Elas permitem identificar:

- O caminho físico do arquivo consultado no S3;
- A camada correspondente;
- O tamanho do arquivo processado.

Instruções de execução

1. Clone o repositório;
2. Abra "Atividade_2_Pipeline_S3_Athena.ipynb" no Google Colab;
3. Inicie o laboratório AWS;
4. Obtenha as credenciais temporárias;
5. Informe as credenciais somente nos campos protegidos do notebook;
6. Execute as células na ordem apresentada;
7. Confira os arquivos gerados no S3;
8. Acesse o Amazon Athena na região "us-east-1";
9. Configure o diretório de resultados como "s3://datalake-mba-10775707/athena-results/";
10. Execute as consultas da pasta "sql/";
11. Confirme que a conciliação retorna "status_integridade = OK".

Execução dos scripts

Os códigos do pipeline estão separados por responsabilidade:

scripts/ingestao_raw.py
scripts/data_quality.py
scripts/processamento_silver.py
scripts/geracao_gold.py

A ordem de execução é:

python scripts/ingestao_raw.py
python scripts/processamento_silver.py
python scripts/geracao_gold.py

O módulo "data_quality.py" é utilizado pelo processamento da Silver para avaliar os pedidos e separar os registros inválidos.

Segurança

As credenciais da AWS e do GitHub não são armazenadas no código-fonte.

Nunca devem ser publicados:

- AWS Access Key ID;
- AWS Secret Access Key;
- AWS Session Token;
- GitHub Personal Access Token.

As credenciais do laboratório AWS são temporárias e expiram ao final da sessão.
"""

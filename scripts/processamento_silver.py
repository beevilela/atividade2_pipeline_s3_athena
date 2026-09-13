
from config import INGEST_DATE
from leitura_raw import carregar_dados_raw
from data_quality import (
    deduplicar_clientes,
    validar_produtos,
    validar_pedidos,
    validar_conciliacao
)
from storage import salvar_json, salvar_parquet


def criar_fato_vendas(pedidos, clientes, produtos):
    """Enriquece os pedidos válidos e calcula o valor total."""

    fato = (
        pedidos
        .merge(
            clientes,
            on="cod_cliente",
            how="inner",
            validate="many_to_one"
        )
        .merge(
            produtos,
            on="product_id",
            how="inner",
            validate="many_to_one"
        )
    )

    fato["valor_total"] = (
        fato["quantidade"] * fato["preco"]
    ).round(2)

    return fato


def executar_processamento_silver():
    print("Iniciando processamento da camada Silver...")

    clientes_raw, produtos_raw, pedidos_raw = carregar_dados_raw()

    # Clientes: deduplicação e padronização
    clientes_validos, clientes_rejeitados = (
        deduplicar_clientes(clientes_raw)
    )

    # Produtos: validação cadastral
    produtos_validos, produtos_rejeitados = (
        validar_produtos(produtos_raw)
    )

    # Pedidos: regras de qualidade e integridade referencial
    pedidos_validos, pedidos_rejeitados = validar_pedidos(
        pedidos_raw,
        clientes_validos,
        produtos_validos
    )

    # Enriquecimento da fato
    fato_vendas = criar_fato_vendas(
        pedidos_validos,
        clientes_validos,
        produtos_validos
    )

    # Conciliação obrigatória
    conciliacao = validar_conciliacao(
        total_raw=len(pedidos_raw),
        total_validos=len(fato_vendas),
        total_rejeitados=len(pedidos_rejeitados)
    )

    # Quarentena
    salvar_json(
        pedidos_rejeitados,
        (
            "quarantine/pedidos_rejeitados/"
            f"data={INGEST_DATE}/rejeitados.json"
        )
    )

    if not clientes_rejeitados.empty:
        salvar_json(
            clientes_rejeitados,
            (
                "quarantine/clientes_duplicados/"
                f"data={INGEST_DATE}/rejeitados.json"
            )
        )

    if not produtos_rejeitados.empty:
        salvar_json(
            produtos_rejeitados,
            (
                "quarantine/produtos_rejeitados/"
                f"data={INGEST_DATE}/rejeitados.json"
            )
        )

    # Camada Silver em Parquet com compressão Snappy
    salvar_parquet(
        clientes_validos,
        (
            "processed/dim_clientes/"
            f"ingest_date={INGEST_DATE}/clientes.parquet"
        )
    )

    salvar_parquet(
        produtos_validos,
        (
            "processed/dim_produtos/"
            f"ingest_date={INGEST_DATE}/produtos.parquet"
        )
    )

    salvar_parquet(
        fato_vendas,
        (
            "processed/fato_vendas/"
            f"ingest_date={INGEST_DATE}/fato_vendas.parquet"
        )
    )

    resultado = {
        "clientes_raw": len(clientes_raw),
        "clientes_silver": len(clientes_validos),
        "clientes_duplicados": len(clientes_rejeitados),
        "produtos_silver": len(produtos_validos),
        "produtos_rejeitados": len(produtos_rejeitados),
        "pedidos_raw": len(pedidos_raw),
        "pedidos_silver": len(fato_vendas),
        "pedidos_rejeitados": len(pedidos_rejeitados),
        "conciliacao": conciliacao
    }

    print("Camada Silver processada com sucesso.")
    print(resultado)

    return {
        "clientes": clientes_validos,
        "produtos": produtos_validos,
        "pedidos_rejeitados": pedidos_rejeitados,
        "fato_vendas": fato_vendas,
        "resumo": resultado
    }


if __name__ == "__main__":
    executar_processamento_silver()

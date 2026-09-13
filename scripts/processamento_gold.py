
import pandas as pd

from config import INGEST_DATE
from storage import ler_parquet_s3, salvar_parquet


def criar_vendas_pais_categoria(fato_vendas: pd.DataFrame):
    """Cria indicadores comerciais por país e categoria."""

    gold = (
        fato_vendas
        .groupby(
            ["nm_pais_cliente", "categoria"],
            as_index=False
        )
        .agg(
            receita_total=("valor_total", "sum"),
            quantidade_vendida=("quantidade", "sum"),
            total_pedidos=("pedido_id", "nunique"),
            clientes_unicos=("cod_cliente", "nunique")
        )
    )

    gold["ticket_medio"] = (
        gold["receita_total"] / gold["total_pedidos"]
    ).round(2)

    gold["receita_total"] = gold["receita_total"].round(2)

    return gold.sort_values(
        "receita_total",
        ascending=False
    ).reset_index(drop=True)


def executar_processamento_gold(fato_vendas=None):
    print("Iniciando processamento da camada Gold...")

    # Permite execução isolada ou pelo orquestrador
    if fato_vendas is None:
        fato_vendas = ler_parquet_s3(
            (
                "processed/fato_vendas/"
                f"ingest_date={INGEST_DATE}/fato_vendas.parquet"
            )
        )

    gold = criar_vendas_pais_categoria(fato_vendas)

    salvar_parquet(
        gold,
        (
            "gold/vendas_pais_categoria/"
            f"ingest_date={INGEST_DATE}/vendas_pais_categoria.parquet"
        )
    )

    resumo = {
        "registros_silver": len(fato_vendas),
        "grupos_gold": len(gold),
        "receita_total": round(gold["receita_total"].sum(), 2),
        "quantidade_vendida": int(
            gold["quantidade_vendida"].sum()
        )
    }

    print("Camada Gold processada com sucesso.")
    print(resumo)

    return {
        "vendas_pais_categoria": gold,
        "resumo": resumo
    }


if __name__ == "__main__":
    executar_processamento_gold()

import pandas as pd

from config import INGEST_DATE
from storage import ler_csv_s3


def validar_colunas(df, colunas, entidade):
    ausentes = set(colunas) - set(df.columns)

    if ausentes:
        raise ValueError(
            f"Colunas ausentes em {entidade}: {sorted(ausentes)}"
        )


def ler_clientes_raw():
    key = (
        f"raw/clientes/"
        f"ingest_date={INGEST_DATE}/"
        f"clientes.csv"
    )

    df = ler_csv_s3(
        key,
        dtype={
            "cod_cliente": "Int64",
            "nm_cliente": "string",
            "nm_pais_cliente": "string",
            "nm_cidade_cliente": "string",
            "nm_rua_cliente": "string",
            "num_casa_cliente": "Int64",
            "telefone_cliente": "string",
            "tp_pessoa": "string",
            "vl_renda": "Float64"
        }
    )

    validar_colunas(
        df,
        [
            "cod_cliente",
            "nm_cliente",
            "nm_pais_cliente",
            "nm_cidade_cliente",
            "nm_rua_cliente",
            "num_casa_cliente",
            "telefone_cliente",
            "dt_nascimento_cliente",
            "dt_atualizacao",
            "tp_pessoa",
            "vl_renda"
        ],
        "clientes"
    )

    df["dt_nascimento_cliente"] = pd.to_datetime(
        df["dt_nascimento_cliente"],
        errors="coerce"
    )

    df["dt_atualizacao"] = pd.to_datetime(
        df["dt_atualizacao"],
        errors="coerce"
    )

    return df


def ler_produtos_raw():
    key = (
        f"raw/produtos/"
        f"ingest_date={INGEST_DATE}/"
        f"produtos.csv"
    )

    df = ler_csv_s3(
        key,
        dtype={
            "product_id": "string",
            "nm_produto": "string",
            "categoria": "string",
            "preco": "Float64"
        }
    )

    validar_colunas(
        df,
        [
            "product_id",
            "nm_produto",
            "categoria",
            "preco"
        ],
        "produtos"
    )

    return df


def ler_pedidos_raw():
    key = (
        f"raw/pedidos/"
        f"ingest_date={INGEST_DATE}/"
        f"pedidos.csv"
    )

    df = ler_csv_s3(
        key,
        dtype={
            "pedido_id": "string",
            "cod_cliente": "Int64",
            "product_id": "string",
            "quantidade": "Int64"
        }
    )

    validar_colunas(
        df,
        [
            "pedido_id",
            "cod_cliente",
            "product_id",
            "quantidade",
            "dt_pedido"
        ],
        "pedidos"
    )

    df["dt_pedido"] = pd.to_datetime(
        df["dt_pedido"],
        errors="coerce"
    )

    return df


def carregar_dados_raw():
    clientes = ler_clientes_raw()
    produtos = ler_produtos_raw()
    pedidos = ler_pedidos_raw()

    print(
        f"Raw carregada: {len(clientes)} clientes, "
        f"{len(produtos)} produtos e "
        f"{len(pedidos)} pedidos."
    )

    return clientes, produtos, pedidos


if __name__ == "__main__":
    carregar_dados_raw()

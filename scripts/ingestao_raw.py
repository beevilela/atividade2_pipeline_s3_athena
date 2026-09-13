from io import StringIO

import numpy as np
import pandas as pd

from config import INGEST_DATE, SOURCE_FILE, validar_configuracao
from storage import salvar_csv


SEMENTE = 42
QTD_PRODUTOS = 120
QTD_PEDIDOS = 10_000


def ler_clientes_origem():
    df = pd.read_excel(
        SOURCE_FILE,
        sheet_name=0
    )

    # Trata o formato original com CSV em uma única coluna.
    if len(df.columns) == 1 and "," in str(df.columns[0]):
        cabecalho = str(df.columns[0])
        linhas = df.iloc[:, 0].dropna().astype(str)

        conteudo = "\n".join(
            [cabecalho] + linhas.tolist()
        )

        df = pd.read_csv(
            StringIO(conteudo)
        )

    return df


def aplicar_schema_clientes(df):
    colunas_obrigatorias = [
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
    ]

    ausentes = set(colunas_obrigatorias) - set(df.columns)

    if ausentes:
        raise ValueError(
            f"Colunas ausentes em clientes: {sorted(ausentes)}"
        )

    df = df[colunas_obgatorias].copy()


def ler_clientes_origem():
    df = pd.read_excel(SOURCE_FILE, sheet_name=0)

    if len(df.columns) == 1 and "," in str(df.columns[0]):
        cabecalho = str(df.columns[0])
        linhas = df.iloc[:, 0].dropna().astype(str)

        conteudo = "\n".join(
            [cabecalho] + linhas.tolist()
        )

        df = pd.read_csv(StringIO(conteudo))

    return df


def aplicar_schema_clientes(df):
    colunas_obrigatorias = [
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
    ]

    ausentes = set(colunas_obrigatorias) - set(df.columns)

    if ausentes:
        raise ValueError(
            f"Colunas ausentes em clientes: {sorted(ausentes)}"
        )

    df = df[colunas_obrigatorias].copy()

    df["cod_cliente"] = pd.to_numeric(
        df["cod_cliente"],
        errors="coerce"
    ).astype("Int64")

    df["num_casa_cliente"] = pd.to_numeric(
        df["num_casa_cliente"],
        errors="coerce"
    ).astype("Int64")

    df["vl_renda"] = pd.to_numeric(
        df["vl_renda"],
        errors="coerce"
    ).astype("Float64")

    df["dt_nascimento_cliente"] = pd.to_datetime(
        df["dt_nascimento_cliente"],
        errors="coerce"
    )

    df["dt_atualizacao"] = pd.to_datetime(
        df["dt_atualizacao"],
        errors="coerce"
    )

    colunas_texto = [
        "nm_cliente",
        "nm_pais_cliente",
        "nm_cidade_cliente",
        "nm_rua_cliente",
        "telefone_cliente",
        "tp_pessoa"
    ]

    for coluna in colunas_texto:
        df[coluna] = (
            df[coluna]
            .astype("string")
            .str.strip()
        )

    return df


def gerar_produtos(rng):
    categorias = {
        "Eletronicos": (150, 6000),
        "Informatica": (50, 4500),
        "Eletrodomesticos": (100, 5000),
        "Moveis": (120, 3500),
        "Casa e Decoracao": (20, 1500),
        "Esporte e Lazer": (30, 2500),
        "Livros": (20, 250),
        "Beleza e Saude": (15, 800)
    }

    categorias_sorteadas = rng.choice(
        list(categorias),
        QTD_PRODUTOS
    )

    produtos = pd.DataFrame({
        "product_id": [
            f"PR{i:04d}"
            for i in range(1, QTD_PRODUTOS + 1)
        ],
        "nm_produto": [
            f"Produto {i:04d}"
            for i in range(1, QTD_PRODUTOS + 1)
        ],
        "categoria": categorias_sorteadas
    })

    produtos["preco"] = [
        round(
            rng.uniform(*categorias[categoria]),
            2
        )
        for categoria in produtos["categoria"]
    ]

    return produtos


def gerar_pedidos(clientes, produtos, rng):
    clientes_existentes = (
        clientes["cod_cliente"]
        .dropna()
        .drop_duplicates()
        .astype(int)
        .to_numpy()
    )

    pedidos = pd.DataFrame({
        "pedido_id": [
            f"PED{i:07d}"
            for i in range(1, QTD_PEDIDOS + 1)
        ],
        "cod_cliente": rng.choice(
            clientes_existentes,
            QTD_PEDIDOS
        ),
        "product_id": rng.choice(
            produtos["product_id"],
            QTD_PEDIDOS
        ),
        "quantidade": rng.integers(
            1,
            7,
            QTD_PEDIDOS
        ),
        "dt_pedido": rng.choice(
            pd.date_range(
                "2026-06-01",
                INGEST_DATE
            ),
            QTD_PEDIDOS
        )
    })

    pedidos["dt_pedido"] = pd.to_datetime(
        pedidos["dt_pedido"]
    ).strftime("%Y-%m-%d")

    indices = rng.choice(
        pedidos.index,
        500,
        replace=False
    )

    pedidos.loc[indices[:100], "quantidade"] = 0
    pedidos.loc[indices[100:200], "quantidade"] = -1
    pedidos.loc[indices[200:350], "cod_cliente"] = 999999
    pedidos.loc[
        indices[350:500],
        "product_id"
    ] = "PR_INEXISTENTE"

    return pedidos


def preparar_clientes_csv(clientes):
    resultado = clientes.copy()

    resultado["dt_nascimento_cliente"] = (
        resultado["dt_nascimento_cliente"]
        .dt.strftime("%Y-%m-%d")
    )

    resultado["dt_atualizacao"] = (
        resultado["dt_atualizacao"]
        .dt.strftime("%Y-%m-%d")
    )

    return resultado


def executar_ingestao_raw():
    validar_configuracao()

    rng = np.random.default_rng(SEMENTE)

    clientes = aplicar_schema_clientes(
        ler_clientes_origem()
    )

    produtos = gerar_produtos(rng)

    pedidos = gerar_pedidos(
        clientes,
        produtos,
        rng
    )

    salvar_csv(
        preparar_clientes_csv(clientes),
        (
            f"raw/clientes/"
            f"ingest_date={INGEST_DATE}/"
            f"clientes.csv"
        )
    )

    salvar_csv(
        produtos,
        (
            f"raw/produtos/"
            f"ingest_date={INGEST_DATE}/"
            f"produtos.csv"
        )
    )

    salvar_csv(
        pedidos,
        (
            f"raw/pedidos/"
            f"ingest_date={INGEST_DATE}/"
            f"pedidos.csv"
        )
    )

    print(
        f"Raw concluída: {len(clientes)} clientes, "
        f"{len(produtos)} produtos e "
        f"{len(pedidos)} pedidos."
    )

    return clientes, produtos, pedidos


if __name__ == "__main__":
    executar_ingestao_raw()

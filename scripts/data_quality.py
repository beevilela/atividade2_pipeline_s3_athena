
import pandas as pd


PAISES_NORMALIZADOS = {
    "United States Minor Outlying Islands": "United States"
}


def deduplicar_clientes(clientes: pd.DataFrame):
    """Mantém o cadastro mais recente de cada cliente."""

    dados = clientes.copy()
    dados["dt_atualizacao"] = pd.to_datetime(
        dados["dt_atualizacao"],
        errors="coerce"
    )

    dados = dados.sort_values(
        ["cod_cliente", "dt_atualizacao"],
        ascending=[True, False]
    )

    mascara_duplicados = dados.duplicated(
        subset=["cod_cliente"],
        keep="first"
    )

    rejeitados = dados.loc[mascara_duplicados].copy()
    rejeitados["motivo_rejeicao"] = (
        "cod_cliente_duplicado_versao_antiga"
    )

    validos = dados.loc[~mascara_duplicados].copy()
    validos["nm_pais_cliente"] = validos[
        "nm_pais_cliente"
    ].replace(PAISES_NORMALIZADOS)

    return (
        validos.reset_index(drop=True),
        rejeitados.reset_index(drop=True)
    )


def validar_produtos(produtos: pd.DataFrame):
    """Separa produtos válidos e inválidos."""

    dados = produtos.copy()
    motivos = pd.Series("", index=dados.index, dtype="object")

    def adicionar_motivo(mascara, motivo):
        motivos.loc[mascara] = motivos.loc[mascara].apply(
            lambda atual: f"{atual} | {motivo}".strip(" |")
        )

    adicionar_motivo(
        dados["product_id"].isna(),
        "product_id_ausente"
    )
    adicionar_motivo(
        dados["product_id"].duplicated(keep=False),
        "product_id_duplicado"
    )
    adicionar_motivo(
        dados["nm_produto"].isna(),
        "nome_produto_ausente"
    )
    adicionar_motivo(
        dados["categoria"].isna(),
        "categoria_ausente"
    )
    adicionar_motivo(
        dados["preco"].isna() | (dados["preco"] <= 0),
        "preco_invalido"
    )

    dados["motivo_rejeicao"] = motivos

    rejeitados = dados[dados["motivo_rejeicao"] != ""].copy()
    validos = dados[dados["motivo_rejeicao"] == ""].copy()
    validos = validos.drop(columns="motivo_rejeicao")

    return (
        validos.reset_index(drop=True),
        rejeitados.reset_index(drop=True)
    )


def validar_pedidos(
    pedidos: pd.DataFrame,
    clientes: pd.DataFrame,
    produtos: pd.DataFrame
):
    """Aplica as regras de Data Quality aos pedidos."""

    dados = pedidos.copy()
    motivos = pd.Series("", index=dados.index, dtype="object")

    clientes_existentes = set(
        clientes["cod_cliente"].dropna()
    )
    produtos_existentes = set(
        produtos["product_id"].dropna()
    )

    def adicionar_motivo(mascara, motivo):
        motivos.loc[mascara] = motivos.loc[mascara].apply(
            lambda atual: f"{atual} | {motivo}".strip(" |")
        )

    adicionar_motivo(
        dados["quantidade"].isna() | (dados["quantidade"] <= 0),
        "quantidade_invalida"
    )
    adicionar_motivo(
        dados["cod_cliente"].isna(),
        "cod_cliente_ausente"
    )
    adicionar_motivo(
        dados["product_id"].isna(),
        "product_id_ausente"
    )
    adicionar_motivo(
        ~dados["cod_cliente"].isin(clientes_existentes),
        "cliente_inexistente"
    )
    adicionar_motivo(
        ~dados["product_id"].isin(produtos_existentes),
        "produto_inexistente"
    )

    dados["motivo_rejeicao"] = motivos

    rejeitados = dados[dados["motivo_rejeicao"] != ""].copy()
    validos = dados[dados["motivo_rejeicao"] == ""].copy()
    validos = validos.drop(columns="motivo_rejeicao")

    return (
        validos.reset_index(drop=True),
        rejeitados.reset_index(drop=True)
    )


def validar_conciliacao(
    total_raw: int,
    total_validos: int,
    total_rejeitados: int
):
    """Garante a integridade quantitativa do processamento."""

    conciliado = total_raw == total_validos + total_rejeitados

    if not conciliado:
        raise ValueError(
            "Falha na conciliação: "
            f"Raw={total_raw}, "
            f"Silver={total_validos}, "
            f"Quarentena={total_rejeitados}"
        )

    return {
        "raw": total_raw,
        "silver": total_validos,
        "quarentena": total_rejeitados,
        "status": "OK"
    }

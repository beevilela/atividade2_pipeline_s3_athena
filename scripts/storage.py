from io import BytesIO
from pathlib import Path

import boto3
import pandas as pd

from config import AWS_REGION, BUCKET_NAME, REPO_ROOT


def obter_cliente_s3():
    return boto3.client(
        "s3",
        region_name=AWS_REGION
    )


def caminho_local(s3_key):
    arquivo = REPO_ROOT / s3_key
    arquivo.parent.mkdir(
        parents=True,
        exist_ok=True
    )
    return arquivo


def salvar_csv(df, s3_key):
    arquivo = caminho_local(s3_key)

    df.to_csv(
        arquivo,
        index=False,
        encoding="utf-8"
    )

    obter_cliente_s3().upload_file(
        str(arquivo),
        BUCKET_NAME,
        s3_key,
        ExtraArgs={"ContentType": "text/csv"}
    )

    return arquivo


def salvar_json(df, s3_key):
    arquivo = caminho_local(s3_key)

    df.to_json(
        arquivo,
        orient="records",
        lines=True,
        force_ascii=False,
        date_format="iso"
    )

    obter_cliente_s3().upload_file(
        str(arquivo),
        BUCKET_NAME,
        s3_key,
        ExtraArgs={"ContentType": "application/json"}
    )

    return arquivo


def salvar_parquet(df, s3_key):
    arquivo = caminho_local(s3_key)

    df.to_parquet(
        arquivo,
        index=False,
        engine="pyarrow",
        compression="snappy"
    )

    obter_cliente_s3().upload_file(
        str(arquivo),
        BUCKET_NAME,
        s3_key
    )

    return arquivo


def ler_csv_s3(s3_key, **kwargs):
    resposta = obter_cliente_s3().get_object(
        Bucket=BUCKET_NAME,
        Key=s3_key
    )

    return pd.read_csv(
        BytesIO(resposta["Body"].read()),
        **kwargs
    )


def ler_parquet_s3(s3_key):
    resposta = obter_cliente_s3().get_object(
        Bucket=BUCKET_NAME,
        Key=s3_key
    )

    return pd.read_parquet(
        BytesIO(resposta["Body"].read()),
        engine="pyarrow"
    )

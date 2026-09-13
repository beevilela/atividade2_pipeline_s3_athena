
import os
from datetime import date
from pathlib import Path


AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

BUCKET_NAME = os.getenv(
    "BUCKET_NAME",
    "datalake-mba-10775707"
)

INGEST_DATE = os.getenv(
    "INGEST_DATE",
    date.today().isoformat()
)

ATHENA_DATABASE = os.getenv(
    "ATHENA_DATABASE",
    "atividade2_pipeline"
)

ATHENA_OUTPUT = os.getenv(
    "ATHENA_OUTPUT",
    f"s3://{BUCKET_NAME}/athena-results/"
)

REPO_ROOT = Path(__file__).resolve().parents[1]

ARQUIVO_REPOSITORIO = (
    REPO_ROOT
    / "dados_origem"
    / "clientes_sinteticos.xlsx"
)

ARQUIVO_COLAB = Path(
    "/content/clientes_sinteticos 1.xlsx"
)

SOURCE_FILE = Path(
    os.getenv(
        "SOURCE_FILE",
        str(
            ARQUIVO_REPOSITORIO
            if ARQUIVO_REPOSITORIO.exists()
            else ARQUIVO_COLAB
        )
    )
)


def validar_configuracao():
    """Valida as configurações necessárias ao pipeline."""

    if not BUCKET_NAME.strip():
        raise ValueError("BUCKET_NAME não foi informado.")

    if not SOURCE_FILE.exists():
        raise FileNotFoundError(
            f"Base de clientes não encontrada: {SOURCE_FILE}"
        )

    if SOURCE_FILE.suffix.lower() != ".xlsx":
        raise ValueError(
            f"A base de clientes deve ser XLSX: {SOURCE_FILE}"
        )

    return {
        "aws_region": AWS_REGION,
        "bucket": BUCKET_NAME,
        "ingest_date": INGEST_DATE,
        "source_file": str(SOURCE_FILE),
        "athena_database": ATHENA_DATABASE,
        "athena_output": ATHENA_OUTPUT
    }


import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

from config import INGEST_DATE, validar_configuracao
from ingestao_raw import executar_ingestao_raw
from processamento_silver import executar_processamento_silver
from processamento_gold import executar_processamento_gold


LOG_DIR = Path(__file__).resolve().parents[1] / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / (
    f"pipeline_{INGEST_DATE}_{datetime.now():%H%M%S}.log"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def executar_pipeline(pular_ingestao=False):
    """Orquestra todas as etapas do pipeline."""

    inicio = datetime.now()

    try:
        logger.info("Iniciando pipeline para %s", INGEST_DATE)

        validar_configuracao()

        if not pular_ingestao:
            logger.info("Etapa 1/3: ingestão da camada Raw")
            executar_ingestao_raw()
        else:
            logger.info("Etapa Raw ignorada por parâmetro")

        logger.info(
            "Etapa 2/3: processamento Silver e quarentena"
        )
        resultado_silver = executar_processamento_silver()

        logger.info("Etapa 3/3: processamento Gold")
        resultado_gold = executar_processamento_gold(
            fato_vendas=resultado_silver["fato_vendas"]
        )

        duracao = (datetime.now() - inicio).total_seconds()

        resumo = {
            "data_processamento": INGEST_DATE,
            "status": "SUCESSO",
            "duracao_segundos": round(duracao, 2),
            "silver": resultado_silver["resumo"],
            "gold": resultado_gold["resumo"]
        }

        logger.info("Pipeline concluído com sucesso")
        logger.info("Resumo: %s", resumo)

        return resumo

    except Exception:
        logger.exception("Falha técnica durante o pipeline")
        raise


def ler_argumentos():
    parser = argparse.ArgumentParser(
        description="Pipeline Medallion com S3 e Athena"
    )

    parser.add_argument(
        "--pular-ingestao",
        action="store_true",
        help="Usa os arquivos Raw que já existem no S3"
    )

    return parser.parse_args()


if __name__ == "__main__":
    argumentos = ler_argumentos()

    executar_pipeline(
        pular_ingestao=argumentos.pular_ingestao
    )

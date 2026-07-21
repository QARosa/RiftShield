"""
Treinamento YOLOv8 para Detecção de Componentes em Diagramas de Arquitetura.

Uso:
    python -m modules.inference.ml-workflow.ml_train_architecture

Dataset esperado em:  backend/datasets/architecture_merged/
Modelo salvo em:      backend/models/architecture_yolo/weights/best.pt
"""

from __future__ import annotations

from pathlib import Path

from ultralytics import YOLO

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
DATASET_DIR = BASE_DIR / "datasets" / "architecture_merged"
MODELS_DIR = BASE_DIR / "models"

DATASET_YAML = DATASET_DIR / "dataset.yaml"


def train():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    model = YOLO("yolov8n.pt")

    results = model.train(
        data=str(DATASET_YAML),
        epochs=100,
        imgsz=640,
        batch=16,
        patience=20,
        project=str(MODELS_DIR),
        name="architecture_yolo",
        exist_ok=True,
        device="cpu",
        workers=4,
    )

    best = MODELS_DIR / "architecture_yolo" / "weights" / "best.pt"
    print("\nTreinamento concluido!")
    print(f"  Dataset: {DATASET_YAML}")
    print(f"  Modelo:  {best}")
    return str(best)


def train_quick():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    model = YOLO("yolov8n.pt")

    results = model.train(
        data=str(DATASET_YAML),
        epochs=10,
        imgsz=640,
        batch=16,
        patience=5,
        project=str(MODELS_DIR),
        name="architecture_yolo_quick",
        exist_ok=True,
        device="cpu",
        workers=4,
    )

    best = MODELS_DIR / "architecture_yolo_quick" / "weights" / "best.pt"
    print("\nTreinamento rapido concluido!")
    print(f"  Modelo: {best}")
    return str(best)


if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("  RiftShield — Treinamento YOLOv8 para Diagramas de Arquitetura")
    print("=" * 60)
    print(f"  Dataset: {DATASET_YAML}")
    print(f"  Modelos: {MODELS_DIR}")

    if not DATASET_YAML.exists():
        print(f"\nERRO: Dataset nao encontrado em {DATASET_YAML}")
        print("Execute primeiro o download e merge com:")
        print("  python backend/download_and_train.py")
        sys.exit(1)

    modo = input("\nEscolha o modo:\n  1 - Completo (100 epocas)\n  2 - Rapido (10 epocas, teste)\n> ").strip()

    if modo == "2":
        train_quick()
    else:
        train()

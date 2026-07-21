from __future__ import annotations

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from modules.inference.models.inference_model import TrainingLog

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
TRAIN_RESULTS_DIR = Path(__file__).resolve().parent.parent / "train_results"
BASE_MODEL_PATH = TRAIN_RESULTS_DIR / "best.pt"
TRAIN_RESULTS_DIR.mkdir(parents=True, exist_ok=True)


async def fine_tune(
    user_id: str,
    epochs: int = 10,
) -> TrainingLog:
    import tempfile
    import yaml
    from modules.inference.dataset.dataset_model import DatasetEntry

    entries = await DatasetEntry.find({"split": "train"}).to_list()
    val_entries = await DatasetEntry.find({"split": "val"}).to_list()

    train_filenames = [e.filename for e in entries + val_entries]

    log = TrainingLog(
        model_type="yolov8n",
        model_name=f"Fine-tune {len(entries) + len(val_entries)} imagens",
        dataset_version="user_upload",
        hyperparameters={"epochs": epochs, "fine_tune": True},
        train_images_count=len(entries),
        val_images_count=len(val_entries),
        classes_count=34,
        trained_filenames=train_filenames,
        status="running",
        started_at=datetime.utcnow(),
    )
    await log.insert()

    try:
        from ultralytics import YOLO

        if not entries:
            raise ValueError("Nenhuma imagem no split Treino. Adicione imagens no Dataset primeiro.")

        if not val_entries and len(entries) >= 2:
            val_count = max(2, len(entries) // 5)
            val_entries = entries[-val_count:]
            entries = entries[:-val_count]
            if not entries:
                entries = val_entries[1:]
                val_entries = val_entries[:1]
        if not val_entries and entries:
            val_entries = entries[:1]
            entries = entries[1:]

        tmpdir = tempfile.mkdtemp()

        train_img = Path(tmpdir) / "train" / "images"
        train_lbl = Path(tmpdir) / "train" / "labels"
        val_img = Path(tmpdir) / "val" / "images"
        val_lbl = Path(tmpdir) / "val" / "labels"
        for d in [train_img, train_lbl, val_img, val_lbl]:
            d.mkdir(parents=True)

        if BASE_MODEL_PATH.exists():
            model = YOLO(str(BASE_MODEL_PATH))
        else:
            model = YOLO("yolov8n.pt")

        names = model.names if hasattr(model, "names") else {}
        nc = len(names) if names else 15

        for entry in entries + val_entries:
            src = Path(entry.image_path)
            if not src.exists():
                continue
            is_val = entry.split == "val"
            dst_img = (val_img if is_val else train_img) / src.name
            dst_lbl = (val_lbl if is_val else train_lbl) / f"{src.stem}.txt"
            shutil.copy(str(src), str(dst_img))
            label_lines = []
            for lbl in (entry.labels or []):
                label_lines.append(f"{lbl.class_id} {lbl.x_center:.6f} {lbl.y_center:.6f} {lbl.width:.6f} {lbl.height:.6f}")
            if not label_lines:
                from PIL import Image as PILImage
                try:
                    with PILImage.open(src) as img_data:
                        iw, ih = img_data.size
                except:
                    _iw, _ih = 640, 640
                label_lines.append(f"0 {0.5:.6f} {0.5:.6f} {1.0:.6f} {1.0:.6f}")
            with open(dst_lbl, "w") as f:
                f.write("\n".join(label_lines) + "\n")

        train_count = len(list(train_img.glob("*")))
        val_count = len(list(val_img.glob("*")))
        if val_count == 0 and train_count > 0:
            for f in list(train_img.glob("*"))[:1]:
                shutil.copy(str(f), str(val_img / f.name))
                lbl_src = train_lbl / f"{f.stem}.txt"
                if lbl_src.exists():
                    shutil.copy(str(lbl_src), str(val_lbl / lbl_src.name))
            val_count = 1
        print(f"FINE-TUNE: train {train_count} imgs | val {val_count} imgs")

        data_yaml_path = os.path.join(tmpdir, "dataset.yaml")
        with open(data_yaml_path, "w") as f:
            yaml.dump({
                "path": tmpdir,
                "train": "train",
                "val": "val",
                "nc": nc,
                "names": list(names.values()) if isinstance(names, dict) else (names if names else [str(i) for i in range(nc)]),
            }, f)

        out_dir = TRAIN_RESULTS_DIR / "fine_tune"
        model.train(
            data=data_yaml_path,
            epochs=epochs,
            imgsz=640,
            batch=8,
            patience=5,
            project=str(out_dir),
            name="run",
            exist_ok=True,
            device="cpu",
            workers=2,
        )

        best = out_dir / "run" / "weights" / "best.pt"
        if best.exists():
            shutil.copy(str(best), str(BASE_MODEL_PATH))
            from modules.inference.services.inference_service import set_active_model
            set_active_model(str(BASE_MODEL_PATH))

        log.status = "completed"
        log.model_path = str(BASE_MODEL_PATH)
        log.metrics = {"fine_tune_epochs": epochs, "train_images": train_count, "val_images": val_count}
        log.completed_at = datetime.utcnow()
        await log.save()

        shutil.rmtree(tmpdir, ignore_errors=True)

    except Exception as e:
        log.status = "failed"
        log.metrics = {"error": str(e)}
        log.completed_at = datetime.utcnow()
        await log.save()

    return log


async def list_training_logs(
    limit: int = 20,
    skip: int = 0,
) -> Tuple[List[TrainingLog], int]:
    total = await TrainingLog.find({}).count()
    items = (
        await TrainingLog.find({})
        .sort(-TrainingLog.created_at)
        .skip(skip)
        .limit(limit)
        .to_list()
    )
    return items, total


async def get_training_log(log_id: str) -> Optional[TrainingLog]:
    return await TrainingLog.get(log_id)


async def activate_model(model_path: str) -> bool:
    from modules.inference.services.inference_service import set_active_model
    set_active_model(model_path)
    return True

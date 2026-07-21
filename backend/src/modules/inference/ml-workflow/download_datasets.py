"""
Download all architecture diagram datasets from Roboflow and merge into one.

Usage:
    python -m modules.inference.ml-workflow.download_datasets

Requires:
    pip install roboflow
    ROBOFLOW_API_KEY environment variable or edit API_KEY below
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import yaml

API_KEY = os.environ.get("ROBOFLOW_API_KEY", "")

ROBOFLOW_DATASETS = [
    {"workspace": "project-v2jjh", "project": "network-topology-diagram", "version": 1},
    {"workspace": "class-diagram-dataset", "project": "class-diagram-detection-covx5", "version": 6},
    {"workspace": "uml-yoxue", "project": "uml-diagram-ml", "version": 5},
    {"workspace": "train-ai-2d5az", "project": "diagram-detection-8ewyo", "version": 8},
    {"workspace": "diagram-automation", "project": "diagram-automation-2", "version": 10},
    {"workspace": "bot-interactivo-tesis", "project": "code-vs-diagram", "version": 1},
    {"workspace": "class-diagram-labeling", "project": "class-diagram-inheritance", "version": 1},
]

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DOWNLOADS_DIR = BASE_DIR / "datasets" / "roboflow_raw"
MERGED_DIR = BASE_DIR / "datasets" / "architecture_merged"


def download_all():
    if not API_KEY:
        raise ValueError("ROBOFLOW_API_KEY environment variable is required")

    from roboflow import Roboflow

    rf = Roboflow(api_key=API_KEY)

    for ds in ROBOFLOW_DATASETS:
        dest = DOWNLOADS_DIR / f"{ds['workspace']}_{ds['project']}"
        if dest.exists():
            print(f"  already exists: {dest.name}")
            continue
        print(f"  downloading: {ds['workspace']}/{ds['project']} v{ds['version']} ...")
        project = rf.workspace(ds["workspace"]).project(ds["project"])
        version = project.version(ds["version"])
        version.download("yolov8", location=str(dest))
        print(f"    done -> {dest}")


def _load_yaml(path: Path):
    with open(path) as f:
        return yaml.safe_load(f)


def merge_datasets():
    if MERGED_DIR.exists():
        shutil.rmtree(MERGED_DIR)

    for split in ["train", "valid"]:
        (MERGED_DIR / split / "images").mkdir(parents=True)
        (MERGED_DIR / split / "labels").mkdir(parents=True)

    merged_names = []
    class_mapping = {}
    next_class_id = 0
    image_counter = 0

    raw_dirs = sorted(DOWNLOADS_DIR.iterdir()) if DOWNLOADS_DIR.exists() else []
    if not raw_dirs:
        print("No downloaded datasets found. Run download_all() first.")
        return

    for ds_dir in raw_dirs:
        if not ds_dir.is_dir():
            continue

        data_yaml_path = ds_dir / "data.yaml"
        if not data_yaml_path.exists():
            continue

        meta = _load_yaml(data_yaml_path)
        names = meta.get("names", [])

        local_mapping = {}
        for class_name in names:
            if class_name not in class_mapping:
                class_mapping[class_name] = next_class_id
                merged_names.append(class_name)
                next_class_id += 1
            local_mapping[class_name] = class_mapping[class_name]

        print(f"Merging: {ds_dir.name} ({len(names)} classes)")

        for split in ["train", "valid"]:
            img_dir = ds_dir / split / "images"
            lbl_dir = ds_dir / split / "labels"

            if not img_dir.exists():
                img_dir = ds_dir / "train" / "images"
                lbl_dir = ds_dir / "train" / "labels"
                if not img_dir.exists():
                    continue

            for img_path in img_dir.glob("*"):
                if img_path.suffix.lower() not in (".png", ".jpg", ".jpeg"):
                    continue

                target_split = "train"
                if split == "valid":
                    target_split = "valid"

                new_name = f"img_{image_counter:06d}{img_path.suffix}"
                shutil.copy(img_path, MERGED_DIR / target_split / "images" / new_name)

                label_path = lbl_dir / f"{img_path.stem}.txt"
                if label_path.exists():
                    new_lines = []
                    with open(label_path) as f:
                        for line in f:
                            parts = line.strip().split()
                            if len(parts) >= 5:
                                orig_class = int(parts[0])
                                if orig_class < len(names):
                                    new_class = local_mapping[names[orig_class]]
                                    parts[0] = str(new_class)
                                    new_lines.append(" ".join(parts))

                    if new_lines:
                        with open(MERGED_DIR / target_split / "labels" / f"img_{image_counter:06d}.txt", "w") as f:
                            f.write("\n".join(new_lines) + "\n")

                image_counter += 1

    data_yaml = {
        "path": str(MERGED_DIR),
        "train": "train",
        "val": "valid",
        "nc": len(merged_names),
        "names": merged_names,
    }

    yaml_path = MERGED_DIR / "dataset.yaml"
    with open(yaml_path, "w") as f:
        yaml.dump(data_yaml, f)

    print("\nMerge complete!")
    print(f"  Total images: {image_counter}")
    print(f"  Total classes: {len(merged_names)}")
    print(f"  Classes: {merged_names}")
    print(f"  Dataset YAML: {yaml_path}")


if __name__ == "__main__":
    print("=== Step 1: Download all datasets ===")
    download_all()

    print("\n=== Step 2: Merge datasets ===")
    merge_datasets()

    print("\nDone! Merged dataset ready for training at:")
    print(f"  {MERGED_DIR}")

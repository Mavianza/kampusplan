"""Penyimpanan JSON yang aman dan ekspor CSV."""

import csv
import json
import os
from pathlib import Path
import tempfile

from .models import Task


def load_tasks(path: Path) -> list[Task]:
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []
    except UnicodeDecodeError as exc:
        raise ValueError(f"Berkas data bukan teks UTF-8 yang valid: {path}") from exc

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Berkas data rusak pada baris {exc.lineno}, kolom {exc.colno}.") from exc
    if not isinstance(payload, list):
        raise ValueError("Format berkas data harus berupa daftar tugas JSON.")

    tasks: list[Task] = []
    seen: set[str] = set()
    for index, item in enumerate(payload, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Data tugas nomor {index} harus berupa objek JSON.")
        task = Task.from_dict(item)
        if task.id in seen:
            raise ValueError(f"ID tugas duplikat ditemukan: {task.id}.")
        seen.add(task.id)
        tasks.append(task)
    return tasks


def save_tasks(path: Path, tasks: list[Task]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps([task.to_dict() for task in tasks], ensure_ascii=False, indent=2) + "\n"
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=path.parent,
            prefix=f".{path.name}.", suffix=".tmp", delete=False
        ) as temporary:
            temporary_name = temporary.name
            temporary.write(content)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_name, path)
    except OSError:
        if temporary_name is not None:
            try:
                os.unlink(temporary_name)
            except OSError:
                pass
        raise


def export_csv(path: Path, tasks: list[Task]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as output:
        writer = csv.DictWriter(
            output,
            fieldnames=["id", "course", "title", "due_date", "priority", "status", "created_at", "completed_at"],
        )
        writer.writeheader()
        writer.writerows(task.to_dict() for task in tasks)


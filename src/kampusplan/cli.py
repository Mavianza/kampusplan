"""Antarmuka baris perintah KampusPlan."""

import argparse
from datetime import date
from pathlib import Path
import sys

from .models import PRIORITIES, Task, local_timestamp
from .storage import export_csv, load_tasks, save_tasks

PRIORITY_ORDER = {"tinggi": 0, "sedang": 1, "rendah": 2}
DEFAULT_DATA = Path.home() / ".kampusplan" / "tasks.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kampusplan",
        description="Catat tugas kuliah dan pantau tenggatnya dari terminal.",
    )
    parser.add_argument(
        "--data", type=Path, default=DEFAULT_DATA,
        help=f"lokasi berkas data JSON (default: {DEFAULT_DATA})",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add", help="tambahkan tugas")
    add.add_argument("course", help="nama mata kuliah")
    add.add_argument("title", help="nama tugas")
    add.add_argument("--due", required=True, help="tenggat dalam format YYYY-MM-DD")
    add.add_argument("--priority", choices=PRIORITIES, default="sedang")

    listing = commands.add_parser("list", help="tampilkan daftar tugas")
    listing.add_argument("--status", choices=("semua", "terbuka", "selesai"), default="semua")
    listing.add_argument("--sort", choices=("tenggat", "prioritas"), default="tenggat")

    commands.add_parser("summary", help="lihat ringkasan tugas")

    done = commands.add_parser("done", help="tandai tugas selesai")
    done.add_argument("id", help="ID tugas")

    remove = commands.add_parser("remove", help="hapus tugas")
    remove.add_argument("id", help="ID tugas")

    export = commands.add_parser("export-csv", help="ekspor semua tugas ke CSV")
    export.add_argument("path", type=Path, help="lokasi berkas CSV keluaran")
    return parser


def _sort_key(task: Task, sort_by: str) -> tuple[object, ...]:
    status_rank = 1 if task.status == "selesai" else 0
    priority_rank = PRIORITY_ORDER[task.priority]
    if sort_by == "prioritas":
        return (status_rank, priority_rank, task.due_date, task.course.casefold(), task.title.casefold())
    return (status_rank, task.due_date, priority_rank, task.course.casefold(), task.title.casefold())


def _print_tasks(tasks: list[Task], sort_by: str) -> None:
    if not tasks:
        print("Belum ada tugas yang cocok dengan filter.")
        return
    print(f"{'ID':<8} {'TENGGAT':<12} {'PRIORITAS':<10} {'STATUS':<9} MATA KULIAH — TUGAS")
    print("-" * 82)
    today = date.today()
    for task in sorted(tasks, key=lambda item: _sort_key(item, sort_by)):
        status = task.status
        if task.status == "terbuka" and task.due_date < today.isoformat():
            status = "terlambat"
        print(f"{task.id:<8} {task.due_date:<12} {task.priority:<10} {status:<9} {task.course} — {task.title}")


def _find_task(tasks: list[Task], task_id: str) -> Task | None:
    normalized_id = task_id.strip().upper()
    return next((task for task in tasks if task.id == normalized_id), None)


def _handle(args: argparse.Namespace) -> int:
    tasks = load_tasks(args.data)

    if args.command == "add":
        task = Task.create(args.course, args.title, args.due, args.priority)
        existing_ids = {item.id for item in tasks}
        while task.id in existing_ids:
            task.id = Task.create(args.course, args.title, args.due, args.priority).id
        tasks.append(task)
        save_tasks(args.data, tasks)
        print(f"Tugas ditambahkan dengan ID {task.id}: {task.course} — {task.title}")
        return 0

    if args.command == "list":
        selected = tasks if args.status == "semua" else [task for task in tasks if task.status == args.status]
        _print_tasks(selected, args.sort)
        return 0

    if args.command == "summary":
        today = date.today().isoformat()
        open_tasks = [task for task in tasks if task.status == "terbuka"]
        overdue = sum(task.due_date < today for task in open_tasks)
        due_today = sum(task.due_date == today for task in open_tasks)
        completed = sum(task.status == "selesai" for task in tasks)
        print("Ringkasan KampusPlan")
        print(f"Terbuka      : {len(open_tasks)}")
        print(f"Tenggat hari ini: {due_today}")
        print(f"Terlambat    : {overdue}")
        print(f"Selesai      : {completed}")
        return 0

    if args.command == "done":
        task = _find_task(tasks, args.id)
        if task is None:
            print(f"ID tugas tidak ditemukan: {args.id}", file=sys.stderr)
            return 1
        if task.status == "selesai":
            print(f"Tugas {task.id} sudah berstatus selesai.")
            return 0
        task.status = "selesai"
        task.completed_at = local_timestamp()
        save_tasks(args.data, tasks)
        print(f"Tugas {task.id} ditandai selesai.")
        return 0

    if args.command == "remove":
        task = _find_task(tasks, args.id)
        if task is None:
            print(f"ID tugas tidak ditemukan: {args.id}", file=sys.stderr)
            return 1
        tasks.remove(task)
        save_tasks(args.data, tasks)
        print(f"Tugas {task.id} dihapus.")
        return 0

    if args.command == "export-csv":
        export_csv(args.path, tasks)
        print(f"{len(tasks)} tugas diekspor ke {args.path}.")
        return 0

    return 2


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return _handle(args)
    except (OSError, ValueError) as exc:
        print(f"Kesalahan: {exc}", file=sys.stderr)
        return 2


import csv
from datetime import date, timedelta
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

from kampusplan.cli import main
from kampusplan.models import Task
from kampusplan.storage import load_tasks, save_tasks


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.data = Path(self.temp_dir.name) / "tasks.json"

    def invoke(self, *args: str) -> tuple[int, str, str]:
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            result = main(["--data", str(self.data), *args])
        return result, stdout.getvalue(), stderr.getvalue()

    def test_add_and_list_task(self) -> None:
        result, output, _ = self.invoke("add", "Prognet", "Buat API", "--due", "2026-11-02", "--priority", "tinggi")
        self.assertEqual(result, 0)
        self.assertIn("ID", output)
        result, output, _ = self.invoke("list", "--status", "terbuka")
        self.assertEqual(result, 0)
        self.assertIn("Prognet — Buat API", output)

    def test_invalid_date_is_reported_without_saving(self) -> None:
        result, _, error = self.invoke("add", "Prognet", "Buat API", "--due", "besok")
        self.assertEqual(result, 2)
        self.assertIn("YYYY-MM-DD", error)
        self.assertEqual(load_tasks(self.data), [])

    def test_done_marks_task_completed(self) -> None:
        save_tasks(self.data, [Task(id="ABC123", course="Prognet", title="Buat API", due_date="2026-11-02", priority="sedang")])
        result, output, _ = self.invoke("done", "abc123")
        self.assertEqual(result, 0)
        self.assertIn("ditandai selesai", output)
        self.assertEqual(load_tasks(self.data)[0].status, "selesai")

    def test_missing_id_returns_nonzero(self) -> None:
        result, _, error = self.invoke("done", "MISS00")
        self.assertEqual(result, 1)
        self.assertIn("tidak ditemukan", error)

    def test_summary_counts_overdue_and_completed(self) -> None:
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        save_tasks(self.data, [
            Task(id="ABC123", course="Prognet", title="Terlambat", due_date=yesterday, priority="tinggi"),
            Task(id="DEF456", course="RO", title="Selesai", due_date=yesterday, priority="rendah", status="selesai"),
        ])
        result, output, _ = self.invoke("summary")
        self.assertEqual(result, 0)
        self.assertIn("Terlambat    : 1", output)
        self.assertIn("Selesai      : 1", output)

    def test_remove_deletes_task(self) -> None:
        save_tasks(self.data, [Task(id="ABC123", course="Prognet", title="Buat API", due_date="2026-11-02", priority="sedang")])
        result, _, _ = self.invoke("remove", "ABC123")
        self.assertEqual(result, 0)
        self.assertEqual(load_tasks(self.data), [])

    def test_export_writes_csv(self) -> None:
        save_tasks(self.data, [Task(id="ABC123", course="Prognet", title="Buat API", due_date="2026-11-02", priority="sedang")])
        output_path = Path(self.temp_dir.name) / "out" / "tasks.csv"
        result, output, _ = self.invoke("export-csv", str(output_path))
        self.assertEqual(result, 0)
        self.assertIn("1 tugas diekspor", output)
        with output_path.open(encoding="utf-8-sig", newline="") as source:
            rows = list(csv.DictReader(source))
        self.assertEqual(rows[0]["id"], "ABC123")


if __name__ == "__main__":
    unittest.main()


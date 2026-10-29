import json
from pathlib import Path
import tempfile
import unittest

from kampusplan.models import Task
from kampusplan.storage import load_tasks, save_tasks


class StorageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.path = Path(self.temp_dir.name) / "nested" / "tasks.json"

    def test_missing_file_returns_empty_list(self) -> None:
        self.assertEqual(load_tasks(self.path), [])

    def test_save_and_load_round_trip(self) -> None:
        task = Task(id="ABC123", course="Riset Operasi", title="Latihan Simpleks", due_date="2026-11-02", priority="tinggi")
        save_tasks(self.path, [task])
        self.assertEqual(load_tasks(self.path), [task])

    def test_invalid_json_has_helpful_error(self) -> None:
        self.path.parent.mkdir(parents=True)
        self.path.write_text("{broken", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Berkas data rusak"):
            load_tasks(self.path)

    def test_non_list_json_is_rejected(self) -> None:
        self.path.parent.mkdir(parents=True)
        self.path.write_text(json.dumps({"tasks": []}), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "daftar tugas"):
            load_tasks(self.path)

    def test_duplicate_ids_are_rejected(self) -> None:
        task = Task(id="ABC123", course="Prognet", title="Demo", due_date="2026-11-02", priority="sedang")
        self.path.parent.mkdir(parents=True)
        self.path.write_text(json.dumps([task.to_dict(), task.to_dict()]), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplikat"):
            load_tasks(self.path)

    def test_invalid_field_type_is_rejected(self) -> None:
        task = Task(id="ABC123", course="Prognet", title="Demo", due_date="2026-11-02", priority="sedang")
        broken = task.to_dict()
        broken["id"] = None
        self.path.parent.mkdir(parents=True)
        self.path.write_text(json.dumps([broken]), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "ID tugas tidak valid"):
            load_tasks(self.path)


if __name__ == "__main__":
    unittest.main()


"""Model dan validasi data tugas KampusPlan."""

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
import secrets

PRIORITIES = ("tinggi", "sedang", "rendah")
STATUSES = ("terbuka", "selesai")


def local_timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


@dataclass
class Task:
    id: str
    course: str
    title: str
    due_date: str
    priority: str
    status: str = "terbuka"
    created_at: str = field(default_factory=local_timestamp)
    completed_at: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.id, str):
            raise ValueError("ID tugas tidak valid.")
        if not isinstance(self.course, str):
            raise ValueError("Nama mata kuliah wajib berupa teks.")
        if not isinstance(self.title, str):
            raise ValueError("Nama tugas wajib berupa teks.")
        self.id = self.id.strip().upper()
        self.course = self.course.strip()
        self.title = self.title.strip()
        if not self.id or not self.id.isalnum():
            raise ValueError("ID tugas tidak valid.")
        if not self.course or len(self.course) > 120:
            raise ValueError("Nama mata kuliah wajib diisi dan maksimal 120 karakter.")
        if not self.title or len(self.title) > 160:
            raise ValueError("Nama tugas wajib diisi dan maksimal 160 karakter.")
        if not isinstance(self.due_date, str):
            raise ValueError("Tanggal harus berupa teks dengan format YYYY-MM-DD.")
        try:
            parsed_due = date.fromisoformat(self.due_date)
        except (TypeError, ValueError) as exc:
            raise ValueError("Tanggal harus memakai format YYYY-MM-DD.") from exc
        self.due_date = parsed_due.isoformat()
        if not isinstance(self.priority, str) or self.priority not in PRIORITIES:
            raise ValueError("Prioritas harus tinggi, sedang, atau rendah.")
        if not isinstance(self.status, str) or self.status not in STATUSES:
            raise ValueError("Status tugas tidak valid.")
        if not isinstance(self.created_at, str) or not self.created_at:
            raise ValueError("Waktu pembuatan tugas tidak valid.")
        if self.completed_at is not None and not isinstance(self.completed_at, str):
            raise ValueError("Waktu penyelesaian tugas tidak valid.")

    @classmethod
    def create(cls, course: str, title: str, due_date: str, priority: str) -> "Task":
        return cls(
            id=secrets.token_hex(3).upper(),
            course=course,
            title=title,
            due_date=due_date,
            priority=priority,
        )

    @classmethod
    def from_dict(cls, value: dict[str, object]) -> "Task":
        required = {"id", "course", "title", "due_date", "priority", "status", "created_at", "completed_at"}
        if not required.issubset(value):
            missing = ", ".join(sorted(required - value.keys()))
            raise ValueError(f"Data tugas tidak lengkap; kolom hilang: {missing}.")
        try:
            return cls(**{key: value[key] for key in required})  # type: ignore[arg-type]
        except TypeError as exc:
            raise ValueError("Format data tugas tidak valid.") from exc

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


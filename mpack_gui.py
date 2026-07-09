from __future__ import annotations

import copy
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, QPointF, QRectF, Qt, QThread, Signal, QSize
from PySide6.QtGui import QBrush, QColor, QDoubleValidator, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateTimeEdit,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from mpack_codec import (
    extract_slotdata_to_sections,
    find_slotdata_files,
    pack_sections_to_slotdata,
    pack_slotdata_with_section_overrides,
    structured_value_to_text,
    text_to_structured_value,
)

SCRIPT_DIR = Path(__file__).resolve().parent
HOME_DIR = Path.home()
DEFAULT_SAVE_CANDIDATES = [
    HOME_DIR / "AppData" / "LocalLow" / "NeuronaGames" / "EsportsManager",
    HOME_DIR / "AppData" / "LocalLow" / "Neurona Games" / "Esports Manager 2026",
]
DEFAULT_WORK_ROOT = SCRIPT_DIR / "workdir"
SECTION_PROFILE_PATH = SCRIPT_DIR / "section_profile.json"
EDITOR_CONFIG_PATH = SCRIPT_DIR / "editor_config.json"
APP_CONFIG_PATH = SCRIPT_DIR / "config.json"
SKILL_VALUE_MIN = 0.0
SKILL_VALUE_MAX = 20.0
SKILL_MONTH_LABELS = {
    "ru": ["февр.", "март", "апр.", "май", "июнь", "июль", "авг.", "сент.", "окт.", "нояб.", "дек.", "янв."],
    "en": ["Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan"],
}

I18N = { 
    "ru": {
        "window_title": "Esports Manager Save Editor",
        "lang_label": "Язык:",
        "save_path": "Папка Save:",
        "slot": "Слот:",
        "slot_archive": "Архивный",
        "browse_save": "Папка Save...",
        "refresh_slots": "Обновить слоты",
        "load": "Загрузить",
        "save_mpack": "Сохранить в mpack",
        "status_wait": "Ожидание загрузки...",
        "status_save_missing": "Папка Save не найдена.",
        "status_no_slots": "Слоты не найдены.",
        "status_slots_found": "Найдено слотов: {count}",
        "status_workdir_loaded": "Загружено из workdir для слота {slot}.",
        "status_loading": "Загрузка и распаковка SlotData...",
        "status_loaded": "Слот {slot} загружен.",
        "status_saved": "Сохранено: {path}",
        "pick_save_title": "Выбери папку Save",
        "no_slot_title": "Нет слота",
        "no_slot_text": "Выбери слот.",
        "load_error_title": "Ошибка загрузки",
        "save_error_title": "Ошибка сохранения",
        "no_data_title": "Нет данных",
        "no_data_text": "Сначала загрузи слот.",
        "success_title": "Успех",
        "success_text": "Сохранено в {path}\nБэкап: {backup}",
        "record": "Запись:",
        "record_search": "Поиск по имени/ID...",
        "record_found": "Найдено: {count}",
        "loading_title": "Загрузка",
        "saving_title": "Сохранение",
        "property": "Свойство {idx}",
        "skill": "Навык {key}",
        "skill_history": "История изменения",
        "skill_end": "Конечное значение",
        "skill_no_data": "Нет данных",
        "skill_not_enough": "Недостаточно точек",
        "skill_no_graph": "Нет графика",
        "skill_month": "М{idx}",
        "slot_empty": "Пусто",
        "slot_pick": "Выбрать...",
        "slot_clear": "Очистить",
        "picker_title": "Выбор записи",
        "picker_search": "Поиск...",
        "picker_pick": "Выбрать",
        "picker_clear": "Очистить слот",
        "picker_cancel": "Отмена",
        "picker_found": "Найдено: {count}",
    },
    "en": {
        "window_title": "Esports Manager Save Editor",
        "lang_label": "Language:",
        "save_path": "Save folder:",
        "slot": "Slot:",
        "slot_archive": "Archived",
        "browse_save": "Save folder...",
        "refresh_slots": "Refresh slots",
        "load": "Load",
        "save_mpack": "Save to mpack",
        "status_wait": "Waiting for load...",
        "status_save_missing": "Save folder not found.",
        "status_no_slots": "No slots found.",
        "status_slots_found": "Slots found: {count}",
        "status_workdir_loaded": "Loaded from workdir for slot {slot}.",
        "status_loading": "Loading and unpacking SlotData...",
        "status_loaded": "Slot {slot} loaded.",
        "status_saved": "Saved: {path}",
        "pick_save_title": "Choose Save folder",
        "no_slot_title": "No slot",
        "no_slot_text": "Select a slot.",
        "load_error_title": "Load error",
        "save_error_title": "Save error",
        "no_data_title": "No data",
        "no_data_text": "Load a slot first.",
        "success_title": "Success",
        "success_text": "Saved to {path}\nBackup: {backup}",
        "record": "Record:",
        "record_search": "Search by name/ID...",
        "record_found": "Found: {count}",
        "loading_title": "Loading",
        "saving_title": "Saving",
        "property": "Property {idx}",
        "skill": "Skill {key}",
        "skill_history": "Change history",
        "skill_end": "Final value",
        "skill_no_data": "No data",
        "skill_not_enough": "Not enough points",
        "skill_no_graph": "No graph",
        "skill_month": "M{idx}",
        "slot_empty": "Empty",
        "slot_pick": "Pick...",
        "slot_clear": "Clear",
        "picker_title": "Pick record",
        "picker_search": "Search...",
        "picker_pick": "Select",
        "picker_clear": "Clear slot",
        "picker_cancel": "Cancel",
        "picker_found": "Found: {count}",
    },
}


def _detect_default_save_root() -> Path:
    dynamic_candidates = list(DEFAULT_SAVE_CANDIDATES) 
    local_low = HOME_DIR / "AppData" / "LocalLow"
    if local_low.exists():
        dynamic_candidates.extend(local_low.glob("**/EsportsManager"))
        dynamic_candidates.extend(local_low.glob("**/Esports Manager 2026"))
    for base in dynamic_candidates:
        direct = base / "Save"
        if direct.exists():
            return direct
        if (base / "SlotMetas.mpack").exists() or any(base.glob("[0-9]*")):
            return base
    return SCRIPT_DIR.parent


DEFAULT_SAVE_ROOT = _detect_default_save_root()


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _dump_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def _default_app_config() -> dict[str, Any]:
    return {
        "save_path": str(DEFAULT_SAVE_ROOT),
        "selected_slot": "",
    }


def _load_app_config() -> dict[str, Any]:
    if not APP_CONFIG_PATH.exists():
        return _default_app_config()
    try:
        loaded = _load_json(APP_CONFIG_PATH)
        if not isinstance(loaded, dict):
            return _default_app_config()
    except Exception:
        return _default_app_config()
    merged = _default_app_config()
    merged.update({k: v for k, v in loaded.items() if isinstance(k, str)})
    return merged


def _save_app_config(cfg: dict[str, Any]) -> None:
    APP_CONFIG_PATH.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")


def _field_to_alias_map(section_key: str) -> dict[str, str]:
    profile = _load_json(SECTION_PROFILE_PATH)
    alias_map = profile.get("field_aliases", {}).get(section_key, {})
    return {field_name: alias for field_name, alias in alias_map.items()}


def _alias_to_field_map(section_key: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for field_name, alias in _field_to_alias_map(section_key).items():
        out[alias] = field_name
    return out


def _load_editor_sections() -> list[dict[str, Any]]:
    raw = _load_json(EDITOR_CONFIG_PATH)
    if isinstance(raw, dict) and isinstance(raw.get("sections"), list):
        return raw["sections"]
    if isinstance(raw, list):
        return [item for item in raw if isinstance(item, dict)]
    return []


def _resolve_org_field_name(section_key: str, alias_or_field: str) -> str:
    if alias_or_field.startswith("field_"):
        return alias_or_field
    return _alias_to_field_map(section_key).get(alias_or_field, alias_or_field)


class EditorLinkedConfig:
    def __init__(
        self,
        *,
        managed_sections: tuple[str, ...],
        org_section_key: str,
        org_team_id_field: str,
        org_roster_fields: tuple[str, ...],
        key_roster_field: str | None,
        roster_members_field: str | None,
    ) -> None:
        self.managed_sections = managed_sections
        self.org_section_key = org_section_key
        self.org_team_id_field = org_team_id_field
        self.org_roster_fields = org_roster_fields
        self.key_roster_field = key_roster_field
        self.roster_members_field = roster_members_field

    @classmethod
    def from_sections(cls, sections: list[dict[str, Any]]) -> EditorLinkedConfig:
        managed_sections = tuple(str(section["key"]) for section in sections if section.get("linked_cache"))

        org_section: dict[str, Any] | None = None
        org_section_key = "11"
        for section in sections:
            linked_context = section.get("linked_context", {})
            if linked_context.get("role") == "organization" or section.get("code") == "organizations":
                org_section = section
                org_section_key = str(section["key"])
                break

        alias_map = _alias_to_field_map(org_section_key)
        linked_context = org_section.get("linked_context", {}) if org_section else {}
        team_id_alias = str(linked_context.get("team_id_alias", "team_id"))
        org_team_id_field = alias_map.get(team_id_alias, _resolve_org_field_name(org_section_key, team_id_alias))

        org_roster_fields: list[str] = []
        key_roster_field: str | None = None
        roster_members_field: str | None = None

        if org_section is not None:
            for item in org_section.get("input", []):
                if item.get("type") != "linked_slots":
                    continue
                alias = str(item.get("alias", ""))
                field_name = alias_map.get(alias)
                if not field_name:
                    continue
                org_roster_fields.append(field_name)

                pick_from = item.get("pick_from_org_alias") or item.get("pick_from_org_field")
                if pick_from:
                    key_roster_field = field_name
                    roster_members_field = _resolve_org_field_name(org_section_key, str(pick_from))

                cleans_alias = item.get("cleans_key_roster_alias")
                if cleans_alias:
                    roster_members_field = field_name
                    key_roster_field = alias_map.get(str(cleans_alias), _resolve_org_field_name(org_section_key, str(cleans_alias)))

        return cls(
            managed_sections=managed_sections,
            org_section_key=org_section_key,
            org_team_id_field=org_team_id_field,
            org_roster_fields=tuple(org_roster_fields),
            key_roster_field=key_roster_field,
            roster_members_field=roster_members_field,
        )


_EDITOR_LINKED_CONFIG: EditorLinkedConfig | None = None


def get_editor_linked_config() -> EditorLinkedConfig:
    global _EDITOR_LINKED_CONFIG
    if _EDITOR_LINKED_CONFIG is None:
        _EDITOR_LINKED_CONFIG = EditorLinkedConfig.from_sections(_load_editor_sections())
    return _EDITOR_LINKED_CONFIG


def _resolve_pick_from_org_field(section_key: str, item: dict[str, Any]) -> str | None:
    pick_from = item.get("pick_from_org_alias") or item.get("pick_from_org_field")
    if not pick_from:
        return None
    return _resolve_org_field_name(section_key, str(pick_from))


def _timestamp_to_qdatetime_data(value: dict[str, Any]) -> str:
    iso = value.get("__timestamp_iso_utc__")
    if isinstance(iso, str) and iso.endswith("Z"):
        return iso[:-1] + "+00:00"
    return "1970-01-01T00:00:00+00:00"


def _qdatetime_to_timestamp_dict(dt_value: datetime) -> dict[str, Any]:
    utc = dt_value.astimezone(timezone.utc)
    unix = utc.timestamp()
    seconds = int(unix)
    nanoseconds = int(round((unix - seconds) * 1_000_000_000))
    return {
        "__timestamp_iso_utc__": utc.isoformat().replace("+00:00", "Z"),
        "__timestamp_seconds__": seconds,
        "__timestamp_nanoseconds__": nanoseconds,
    }


class LoadingOverlay(QWidget):
    def __init__(self, parent: QWidget, message: str) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 140);")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        box = QWidget()
        box.setStyleSheet("background-color: #2b2b2b; border-radius: 8px; padding: 16px;")
        box_layout = QVBoxLayout(box)
        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignCenter)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setFixedWidth(280)
        box_layout.addWidget(self.label)
        box_layout.addWidget(self.progress)
        layout.addWidget(box)

    def set_message(self, message: str) -> None:
        self.label.setText(message)

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        if self.parentWidget() is not None:
            self.setGeometry(self.parentWidget().rect())
        super().resizeEvent(event)


class LoadWorker(QObject):
    finished = Signal(dict)
    failed = Signal(str)

    def __init__(self, save_root: Path, slot_id: str, work_root: Path, use_existing_workdir: bool = False) -> None:
        super().__init__()
        self.save_root = save_root
        self.slot_id = slot_id
        self.work_root = work_root
        self.use_existing_workdir = use_existing_workdir

    def run(self) -> None:
        try:
            source_mpack = self.save_root / self.slot_id / "SlotData.mpack"
            if not source_mpack.exists():
                raise FileNotFoundError(f"SlotData.mpack not found: {source_mpack}") 
            base_mpack_bytes = source_mpack.read_bytes()
            if self.use_existing_workdir:
                slot_work = self.work_root / self.slot_id
                readable_json = slot_work / "SlotData.readable.json"
                sections_dir = slot_work / "SlotData.readable_sections"
                manifest = sections_dir / "manifest.json"
                if not sections_dir.exists() or not manifest.exists():
                    raise FileNotFoundError(f"Workdir not found for slot {self.slot_id}: {sections_dir}")
                ctx = {
                    "source_mpack": source_mpack,
                    "slot_work": slot_work,
                    "readable_json": readable_json,
                    "sections_dir": sections_dir,
                    "manifest": manifest,
                    "loaded_from_workdir": True,
                    "base_mpack_bytes": base_mpack_bytes,
                }
            else:
                ctx = extract_slotdata_to_sections(
                    save_root=self.save_root,
                    slot_id=self.slot_id,
                    work_root=self.work_root,
                    profile_path=SECTION_PROFILE_PATH,
                )
                ctx["loaded_from_workdir"] = False
                ctx["base_mpack_bytes"] = base_mpack_bytes
            self.finished.emit(ctx)
        except Exception as exc:
            self.failed.emit(str(exc))


class SaveWorker(QObject):
    finished = Signal(str)
    failed = Signal(str)

    def __init__(self, loaded_ctx: dict[str, Path], managed_section_keys: list[str]) -> None:
        super().__init__()
        self.loaded_ctx = loaded_ctx
        self.managed_section_keys = managed_section_keys

    def run(self) -> None:
        try:
            sections_dir = self.loaded_ctx["sections_dir"]
            source_mpack = self.loaded_ctx["source_mpack"]
            base_mpack_bytes = self.loaded_ctx.get("base_mpack_bytes")
            if not isinstance(base_mpack_bytes, (bytes, bytearray)):
                raise ValueError("Missing base SlotData snapshot for safe save.")
            backup_path = source_mpack.with_suffix(".mpack.bak")
            if not backup_path.exists():
                backup_path.write_bytes(bytes(base_mpack_bytes))
            pack_slotdata_with_section_overrides(
                bytes(base_mpack_bytes),
                sections_dir,
                source_mpack,
                self.managed_section_keys,
                output_readable_json=self.loaded_ctx["readable_json"],
            )
            self.finished.emit(str(source_mpack))
        except Exception as exc:
            self.failed.emit(str(exc))


def _record_label(item: Any, idx: int) -> str:
    if isinstance(item, dict):
        entry_key = item.get("__entry_key")
        if entry_key is not None:
            return f"{idx}: {entry_key}"
        title = str(item.get("field_1") or item.get("field_0") or f"#{idx}")
        extra = item.get("field_2")
        if extra and str(extra) not in title:
            return f"{idx}: {title} ({extra})"
        return f"{idx}: {title}"
    return f"{idx}: #{idx}" 


def _record_search_blob(item: Any, idx: int) -> str:
    if not isinstance(item, dict):
        return str(idx)
    parts = [str(idx)]
    entry_key = item.get("__entry_key")
    if entry_key is not None:
        parts.append(str(entry_key))
    for key in ("field_0", "field_1", "field_2", "field_3", "field_6"):
        value = item.get(key)
        if value is not None:
            parts.append(str(value))
    return " ".join(parts).lower()


def _skill_month_labels(lang: str, count: int) -> list[str]: 
    labels = SKILL_MONTH_LABELS.get(lang) or SKILL_MONTH_LABELS["en"]
    if count <= len(labels):
        return labels[:count]
    return [I18N[lang]["skill_month"].format(idx=i + 1) for i in range(count)]


def _catmull_rom_points(points: list[QPointF], segments: int = 12) -> list[QPointF]:
    if len(points) < 2:
        return points
    smooth: list[QPointF] = []
    for i in range(len(points) - 1):
        p0 = points[i - 1] if i > 0 else points[i]
        p1 = points[i]
        p2 = points[i + 1]
        p3 = points[i + 2] if i + 2 < len(points) else points[i + 1]
        for step in range(segments):
            t = step / segments
            t2 = t * t
            t3 = t2 * t
            x = 0.5 * (
                (2 * p1.x())
                + (-p0.x() + p2.x()) * t
                + (2 * p0.x() - 5 * p1.x() + 4 * p2.x() - p3.x()) * t2
                + (-p0.x() + 3 * p1.x() - 3 * p2.x() + p3.x()) * t3
            )
            y = 0.5 * (
                (2 * p1.y())
                + (-p0.y() + p2.y()) * t
                + (2 * p0.y() - 5 * p1.y() + 4 * p2.y() - p3.y()) * t2
                + (-p0.y() + 3 * p1.y() - 3 * p2.y() + p3.y()) * t3
            )
            smooth.append(QPointF(x, y))
    smooth.append(points[-1])
    return smooth


class SkillHistoryChart(QWidget):
    def __init__(self, lang: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.lang = lang
        self.points: list[float] = []
        self.message = ""
        self.setMinimumHeight(190)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def sizeHint(self) -> QSize:  # type: ignore[override]
        return QSize(420, 190)

    def set_data(self, points: list[float] | None, message: str = "") -> None:
        self.points = list(points or [])
        self.message = message
        self.update()

    def _chart_rect(self) -> QRectF:
        return QRectF(42, 24, max(1.0, self.width() - 54), max(1.0, self.height() - 58))

    def _value_to_y(self, value: float, chart: QRectF) -> float:
        ratio = (value - SKILL_VALUE_MIN) / (SKILL_VALUE_MAX - SKILL_VALUE_MIN)
        ratio = max(0.0, min(1.0, ratio))
        return chart.bottom() - ratio * chart.height()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.fillRect(self.rect(), QColor(24, 28, 36))

        chart = self._chart_rect()
        frame_pen = QPen(QColor(120, 130, 150, 180), 1)
        painter.setPen(frame_pen)
        painter.drawRect(chart)

        corner = 10
        for x, y in (
            (chart.left(), chart.top()),
            (chart.right(), chart.top()),
            (chart.left(), chart.bottom()),
            (chart.right(), chart.bottom()),
        ):
            painter.drawLine(x, y, x + (corner if x == chart.left() else -corner), y)
            painter.drawLine(x, y, x, y + (corner if y == chart.top() else -corner))

        if not self.points:
            painter.setPen(QColor(170, 175, 185))
            painter.drawText(chart, Qt.AlignmentFlag.AlignCenter, self.message or "-")
            painter.end()
            return

        painter.setPen(QColor(210, 215, 225))
        painter.drawText(
            QRectF(chart.left(), 4, chart.width(), 18),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            I18N[self.lang]["skill_history"],
        )

        for tick in range(int(SKILL_VALUE_MIN), int(SKILL_VALUE_MAX) + 1, 2):
            y = self._value_to_y(float(tick), chart)
            grid_pen = QPen(QColor(70, 78, 95, 120), 1, Qt.PenStyle.DashLine)
            painter.setPen(grid_pen)
            painter.drawLine(chart.left(), y, chart.right(), y)
            painter.setPen(QColor(150, 158, 172))
            painter.drawText(QRectF(4, y - 8, 34, 16), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, str(tick))

        count = len(self.points)
        step_x = chart.width() / max(count, 1)
        bar_width = max(6.0, step_x * 0.55)
        plot_points: list[QPointF] = []

        for idx, value in enumerate(self.points):
            center_x = chart.left() + step_x * (idx + 0.5)
            y = self._value_to_y(value, chart)
            plot_points.append(QPointF(center_x, y))
            bar_rect = QRectF(center_x - bar_width / 2, y, bar_width, chart.bottom() - y)
            painter.fillRect(bar_rect, QColor(95, 45, 140, 90))

        smooth_points = _catmull_rom_points(plot_points)
        if len(smooth_points) >= 2:
            line_path = QPainterPath()
            line_path.moveTo(smooth_points[0])
            for point in smooth_points[1:]:
                line_path.lineTo(point)

            fill_path = QPainterPath(line_path)
            fill_path.lineTo(smooth_points[-1].x(), chart.bottom())
            fill_path.lineTo(smooth_points[0].x(), chart.bottom())
            fill_path.closeSubpath()
            gradient = QLinearGradient(0, chart.top(), 0, chart.bottom())
            gradient.setColorAt(0.0, QColor(255, 70, 190, 120))
            gradient.setColorAt(1.0, QColor(120, 40, 150, 10))
            painter.fillPath(fill_path, QBrush(gradient))

            glow_pen = QPen(QColor(255, 90, 200, 70), 5)
            glow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(glow_pen)
            painter.drawPath(line_path)
            line_pen = QPen(QColor(255, 95, 205), 2.2)
            line_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(line_pen)
            painter.drawPath(line_path)

        month_labels = _skill_month_labels(self.lang, count)
        painter.setPen(QColor(145, 152, 168))
        for idx, label in enumerate(month_labels):
            center_x = chart.left() + step_x * (idx + 0.5)
            painter.drawText(
                QRectF(center_x - step_x / 2, chart.bottom() + 6, step_x, 18),
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                label,
            )

        painter.end()


class SkillEditorWidget(QGroupBox):
    def __init__(self, title: str, lang: str, parent: QWidget | None = None) -> None:
        super().__init__(title, parent)
        self.lang = lang
        self.chart = SkillHistoryChart(lang)
        self.end_edit = QLineEdit()
        skill_validator = QDoubleValidator(SKILL_VALUE_MIN, SKILL_VALUE_MAX, 2) 
        skill_validator.setNotation(QDoubleValidator.StandardNotation)
        self.end_edit.setValidator(skill_validator)
        self.end_edit.setPlaceholderText(
            f"{I18N[self.lang]['skill_end']} ({SKILL_VALUE_MIN:g}–{SKILL_VALUE_MAX:g})"
        )
        layout = QVBoxLayout(self)
        layout.addWidget(self.chart)
        form = QFormLayout()
        form.addRow(I18N[self.lang]["skill_end"], self.end_edit)
        layout.addLayout(form)
        self.data_obj: dict[str, Any] | None = None
        self.end_key: str | None = None

    def bind_data(self, data_obj: dict[str, Any] | None) -> None:
        self.data_obj = data_obj
        if not isinstance(data_obj, dict):
            self.chart.set_data([], I18N[self.lang]["skill_no_data"])
            self.end_edit.setText("")
            self.end_key = None
            return
        numeric_keys = sorted(
            [k for k in data_obj.keys() if k.startswith("field_") and k[6:].isdigit()],
            key=lambda x: int(x.split("_")[1]),
        )
        if len(numeric_keys) < 2:
            self.chart.set_data([], I18N[self.lang]["skill_not_enough"])
            self.end_edit.setText("")
            self.end_key = None
            return
        self.end_key = numeric_keys[-1]
        graph_keys = numeric_keys[1:-1]
        points = [float(data_obj[k]) for k in graph_keys if isinstance(data_obj.get(k), (int, float))]
        if points:
            self.chart.set_data(points)
        else:
            self.chart.set_data([], I18N[self.lang]["skill_no_graph"])
        end_val = data_obj.get(self.end_key)
        self.end_edit.setText(str(end_val if end_val is not None else ""))

    def apply_changes(self) -> None:
        if self.data_obj is None or self.end_key is None:
            return
        text = self.end_edit.text().strip()
        if not text:
            return
        value = max(SKILL_VALUE_MIN, min(SKILL_VALUE_MAX, float(text)))
        self.data_obj[self.end_key] = value
        self.end_edit.setText(str(value))


class LinkedSectionContext:
    def __init__(self, sections_dir: Path, linked_config: EditorLinkedConfig | None = None) -> None:
        self.sections_dir = sections_dir
        self.linked_config = linked_config or get_editor_linked_config()
        self._cache: dict[str, list[Any]] = {}

    def get_section(self, section_key: str) -> list[Any]:
        if section_key not in self._cache:
            path = self.sections_dir / f"section_{section_key}.json"
            data = _load_json(path)
            self._cache[section_key] = data if isinstance(data, list) else []
        return self._cache[section_key]

    def find_org_by_team_id(self, team_id: str) -> dict[str, Any] | None:
        needle = team_id.strip()
        if not needle:
            return None
        team_field = self.linked_config.org_team_id_field
        for org in self.get_section(self.linked_config.org_section_key):
            if not isinstance(org, dict):
                continue
            if str(org.get(team_field, "")).strip() == needle:
                return org
        return None

    def save_managed_sections(self) -> None:
        for section_key in self.linked_config.managed_sections:
            if section_key not in self._cache:
                continue
            path = self.sections_dir / f"section_{section_key}.json"
            _dump_json(path, self._cache[section_key])


def _entity_store_value(entity: dict[str, Any], store_field: str) -> str:
    return str(entity.get(store_field, "") or "").strip()


def _swap_entity_team_contract(
    left: dict[str, Any],
    right: dict[str, Any],
    *,
    team_field: str,
    contract_field: str | None,
) -> None:
    left_team = left.get(team_field)
    right_team = right.get(team_field)
    left[team_field] = right_team
    right[team_field] = left_team

    if not contract_field:
        return

    left_contract = left.get(contract_field)
    right_contract = right.get(contract_field)
    left[contract_field] = copy.deepcopy(right_contract) if isinstance(right_contract, dict) else right_contract
    right[contract_field] = copy.deepcopy(left_contract) if isinstance(left_contract, dict) else left_contract


def _roster_slot_keys(slots_obj: dict[str, Any]) -> list[str]:
    keys = [k for k in slots_obj if isinstance(k, str) and k.startswith("field_") and k[6:].isdigit()]
    return sorted(keys, key=lambda x: int(x.split("_")[1]))


def _find_entity_roster_slot(
    org: dict[str, Any],
    entity_value: str,
    match_fields: list[str],
    *,
    source_section_data: list[Any],
    org_roster_fields: tuple[str, ...],
) -> tuple[str, str] | None:
    entity = _find_entity_by_value(source_section_data, entity_value, match_fields)
    if entity is None:
        return None
    store_values = {_entity_store_value(entity, key) for key in match_fields if key.startswith("field_")}
    store_values.add(entity_value.strip())
    for roster_field in org_roster_fields:
        roster = org.get(roster_field)
        if not isinstance(roster, dict):
            continue
        for slot_key in _roster_slot_keys(roster):
            slot_value = str(roster.get(slot_key, "") or "").strip()
            if slot_value and slot_value in store_values:
                return roster_field, slot_key
    return None


def _remove_entity_from_org_rosters(
    org: dict[str, Any],
    entity_value: str,
    match_fields: list[str],
    source_section_data: list[Any],
    *,
    org_roster_fields: tuple[str, ...],
    except_field: str | None = None,
    except_key: str | None = None,
) -> None:
    entity = _find_entity_by_value(source_section_data, entity_value, match_fields)
    values = {entity_value.strip()}
    if entity is not None:
        for key in match_fields:
            values.add(_entity_store_value(entity, key))
    for roster_field in org_roster_fields:
        roster = org.get(roster_field)
        if not isinstance(roster, dict):
            continue
        for slot_key in _roster_slot_keys(roster):
            if roster_field == except_field and slot_key == except_key:
                continue
            if str(roster.get(slot_key, "") or "").strip() in values:
                roster.pop(slot_key, None)


def _remove_entity_from_key_roster(
    org: dict[str, Any],
    entity_value: str,
    match_fields: list[str],
    source_section_data: list[Any],
    *,
    key_roster_field: str,
) -> None:
    entity = _find_entity_by_value(source_section_data, entity_value, match_fields)
    values = {entity_value.strip()}
    if entity is not None:
        for key in match_fields:
            values.add(_entity_store_value(entity, key))
    key_roster = org.get(key_roster_field)
    if not isinstance(key_roster, dict):
        return
    for slot_key in _roster_slot_keys(key_roster):
        if str(key_roster.get(slot_key, "") or "").strip() in values:
            key_roster.pop(slot_key, None)


def _allowed_ids_from_org_field(org: dict[str, Any], roster_field: str) -> set[str]:
    roster = org.get(roster_field)
    if not isinstance(roster, dict):
        return set()
    return {str(value).strip() for value in roster.values() if str(value).strip()}


def _apply_roster_assignment(
    linked_context: LinkedSectionContext,
    org: dict[str, Any],
    roster_field: str,
    slot_index: int,
    new_entity: dict[str, Any] | None,
    link_cfg: dict[str, Any],
    *,
    pick_from_org_field: str | None = None,
) -> None:
    linked_config = linked_context.linked_config
    source_section = str(link_cfg["source_section"])
    store_field = str(link_cfg["store_field"])
    team_field = str(link_cfg["team_field"])
    match_fields = list(link_cfg.get("match_fields", [store_field]))
    contract_field = link_cfg.get("contract_field")
    section_data = linked_context.get_section(source_section)
    org_roster_fields = linked_config.org_roster_fields
    key_roster_field = linked_config.key_roster_field
    roster_members_field = linked_config.roster_members_field

    roster = org.setdefault(roster_field, {})
    if not isinstance(roster, dict):
        roster = {}
        org[roster_field] = roster
    slot_key = f"field_{slot_index}"
    team_id = str(org.get(linked_config.org_team_id_field, "") or "").strip()
    old_value = str(roster.get(slot_key, "") or "").strip()
    old_entity = _find_entity_by_value(section_data, old_value, match_fields) if old_value else None

    if pick_from_org_field:
        allowed = _allowed_ids_from_org_field(org, pick_from_org_field)
        if new_entity is None:
            roster.pop(slot_key, None)
            return
        new_value = _entity_store_value(new_entity, store_field)
        if new_value not in allowed:
            return
        roster[slot_key] = new_value
        return

    if new_entity is None:
        if old_entity is not None and str(old_entity.get(team_field, "") or "").strip() == team_id:
            old_entity[team_field] = ""
        roster.pop(slot_key, None)
        if roster_members_field and roster_field == roster_members_field and old_value and key_roster_field:
            _remove_entity_from_key_roster(
                org,
                old_value,
                match_fields,
                section_data,
                key_roster_field=key_roster_field,
            )
        return

    new_value = _entity_store_value(new_entity, store_field)
    if not new_value:
        return

    new_entity_team = str(new_entity.get(team_field, "") or "").strip()

    if old_entity is not None and old_entity is not new_entity:
        _swap_entity_team_contract(
            old_entity,
            new_entity,
            team_field=team_field,
            contract_field=str(contract_field) if contract_field else None,
        )
        if new_entity_team and new_entity_team != team_id:
            other_org = linked_context.find_org_by_team_id(new_entity_team)
            if other_org is not None:
                found = _find_entity_roster_slot(
                    other_org,
                    new_value,
                    match_fields,
                    source_section_data=section_data,
                    org_roster_fields=org_roster_fields,
                )
                old_out_value = _entity_store_value(old_entity, store_field)
                if found is not None:
                    other_field, other_key = found
                    other_roster = other_org.setdefault(other_field, {})
                    if isinstance(other_roster, dict) and old_out_value:
                        other_roster[other_key] = old_out_value
                elif old_out_value:
                    mirror = other_org.setdefault(roster_field, {})
                    if isinstance(mirror, dict):
                        mirror[slot_key] = old_out_value
        _remove_entity_from_org_rosters(
            org,
            new_value,
            match_fields,
            section_data,
            org_roster_fields=org_roster_fields,
            except_field=roster_field,
            except_key=slot_key,
        )
    elif old_entity is None:
        if new_entity_team and new_entity_team != team_id:
            other_org = linked_context.find_org_by_team_id(new_entity_team)
            if other_org is not None:
                found = _find_entity_roster_slot(
                    other_org,
                    new_value,
                    match_fields,
                    source_section_data=section_data,
                    org_roster_fields=org_roster_fields,
                )
                if found is not None:
                    other_field, other_key = found
                    other_roster = other_org.setdefault(other_field, {})
                    if isinstance(other_roster, dict):
                        other_roster.pop(other_key, None)
        new_entity[team_field] = team_id
        _remove_entity_from_org_rosters(
            org,
            new_value,
            match_fields,
            section_data,
            org_roster_fields=org_roster_fields,
            except_field=roster_field,
            except_key=slot_key,
        )
    else:
        _remove_entity_from_org_rosters(
            org,
            new_value,
            match_fields,
            section_data,
            org_roster_fields=org_roster_fields,
            except_field=roster_field,
            except_key=slot_key,
        )

    roster[slot_key] = new_value

    if (
        roster_members_field
        and key_roster_field
        and roster_field == roster_members_field
        and old_value
        and old_value != new_value
    ):
        _remove_entity_from_key_roster(
            org,
            old_value,
            match_fields,
            section_data,
            key_roster_field=key_roster_field,
        )

    if roster_members_field and key_roster_field:
        allowed_key = _allowed_ids_from_org_field(org, roster_members_field)
        key_roster = org.get(key_roster_field)
        if isinstance(key_roster, dict) and allowed_key:
            for key in _roster_slot_keys(key_roster):
                if str(key_roster.get(key, "") or "").strip() not in allowed_key:
                    key_roster.pop(key, None)


def _entity_label(item: dict[str, Any], display_fields: list[str]) -> str:
    parts: list[str] = []
    for key in display_fields:
        value = item.get(key)
        if value is not None and str(value).strip():
            parts.append(str(value))
    if not parts:
        parts.append(str(item.get("field_0", "?")))
    return " / ".join(parts)


def _entity_search_blob(item: dict[str, Any], display_fields: list[str]) -> str:
    parts = [_entity_label(item, display_fields)]
    for key in ("field_0", "field_1", "field_2", "field_3", "field_6"):
        value = item.get(key)
        if value is not None:
            parts.append(str(value))
    return " ".join(parts).lower()


def _find_entity_by_value(
    section_data: list[Any],
    value: str,
    match_fields: list[str],
) -> dict[str, Any] | None:
    needle = value.strip()
    if not needle:
        return None
    for item in section_data:
        if not isinstance(item, dict):
            continue
        for key in match_fields:
            if str(item.get(key, "")).strip() == needle:
                return item
    return None


class EntityPickerDialog(QDialog):
    def __init__(
        self,
        lang: str,
        title: str,
        section_data: list[Any],
        display_fields: list[str],
        parent: QWidget | None = None,
        *,
        allowed_ids: set[str] | None = None,
        store_field: str = "field_0",
    ) -> None:
        super().__init__(parent)
        self.lang = lang
        self.section_data = section_data
        self.display_fields = display_fields
        self.allowed_ids = allowed_ids
        self.store_field = store_field
        self.selected_index: int | None = None
        self.setWindowTitle(title)
        self.resize(560, 520)

        layout = QVBoxLayout(self)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(I18N[lang]["picker_search"])
        self.search_edit.textChanged.connect(self._filter)
        layout.addWidget(self.search_edit)

        self.count_label = QLabel()
        layout.addWidget(self.count_label)

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self._accept_selection)
        layout.addWidget(self.list_widget, 1)

        buttons = QDialogButtonBox()
        pick_btn = buttons.addButton(I18N[lang]["picker_pick"], QDialogButtonBox.AcceptRole)
        clear_btn = buttons.addButton(I18N[lang]["picker_clear"], QDialogButtonBox.ActionRole)
        cancel_btn = buttons.addButton(I18N[lang]["picker_cancel"], QDialogButtonBox.RejectRole)
        pick_btn.clicked.connect(self._accept_selection)
        clear_btn.clicked.connect(self._clear_selection)
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(buttons)

        self._entries: list[tuple[int, str, str]] = []
        self._rebuild_entries()
        self._filter("")

    def _rebuild_entries(self) -> None:
        self._entries.clear()
        for idx, item in enumerate(self.section_data):
            if not isinstance(item, dict):
                continue
            if self.allowed_ids is not None:
                value = str(item.get(self.store_field, "") or "").strip()
                if value not in self.allowed_ids:
                    continue
            label = _entity_label(item, self.display_fields)
            blob = _entity_search_blob(item, self.display_fields)
            self._entries.append((idx, label, blob))

    def _filter(self, query: str) -> None:
        needle = query.strip().lower()
        self.list_widget.clear()
        shown = 0
        for data_idx, label, blob in self._entries:
            if needle and needle not in blob and needle not in label.lower():
                continue
            self.list_widget.addItem(label)
            row = self.list_widget.count() - 1
            self.list_widget.item(row).setData(Qt.UserRole, data_idx)
            shown += 1
        self.count_label.setText(I18N[self.lang]["picker_found"].format(count=shown))

    def _accept_selection(self) -> None:
        item = self.list_widget.currentItem()
        if item is None:
            return
        data = item.data(Qt.UserRole)
        if data is None:
            return
        self.selected_index = int(data)
        self.accept()

    def _clear_selection(self) -> None:
        self.selected_index = None
        self.accept()


class LinkedSlotsWidget(QGroupBox):
    def __init__(
        self,
        lang: str,
        slot_count: int,
        link_cfg: dict[str, Any],
        linked_context: LinkedSectionContext,
        roster_field: str,
        get_org_record: Any,
        get_slots_obj: Any,
        set_slots_obj: Any,
        on_roster_changed: Any | None = None,
        pick_from_org_field: str | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.lang = lang
        self.slot_count = slot_count
        self.link_cfg = link_cfg
        self.linked_context = linked_context
        self.roster_field = roster_field
        self.get_org_record = get_org_record
        self.get_slots_obj = get_slots_obj
        self.set_slots_obj = set_slots_obj
        self.on_roster_changed = on_roster_changed
        self.pick_from_org_field = pick_from_org_field
        self.slot_buttons: list[QPushButton] = []

        grid = QGridLayout(self)
        for idx in range(slot_count):
            btn = QPushButton(I18N[lang]["slot_empty"])
            btn.clicked.connect(lambda _checked=False, i=idx: self._open_picker(i))
            self.slot_buttons.append(btn)
            grid.addWidget(btn, idx // 2, idx % 2)

    def refresh(self) -> None:
        slots_obj = self.get_slots_obj()
        if not isinstance(slots_obj, dict):
            slots_obj = {}
        store_field = str(self.link_cfg.get("store_field", "field_0"))
        display_fields = list(self.link_cfg.get("display_fields", ["field_1", "field_2", "field_3"]))
        source_section = str(self.link_cfg.get("source_section", "10"))
        match_fields = list(self.link_cfg.get("match_fields", [store_field, "field_1"]))
        section_data = self.linked_context.get_section(source_section)

        for idx, btn in enumerate(self.slot_buttons):
            slot_key = f"field_{idx}"
            value = slots_obj.get(slot_key)
            if value is None or str(value).strip() == "":
                btn.setText(I18N[self.lang]["slot_empty"])
                continue
            entity = _find_entity_by_value(section_data, str(value), match_fields)
            if entity is not None:
                btn.setText(_entity_label(entity, display_fields))
            else:
                btn.setText(str(value))

    def _open_picker(self, slot_index: int) -> None:
        org = self.get_org_record()
        if not isinstance(org, dict):
            return

        source_section = str(self.link_cfg.get("source_section", "10"))
        display_fields = list(self.link_cfg.get("display_fields", ["field_1", "field_2", "field_3"]))
        store_field = str(self.link_cfg.get("store_field", "field_0"))
        section_data = self.linked_context.get_section(source_section)

        allowed_ids: set[str] | None = None
        if self.pick_from_org_field:
            allowed_ids = _allowed_ids_from_org_field(org, self.pick_from_org_field)

        dialog = EntityPickerDialog(
            self.lang,
            I18N[self.lang]["picker_title"],
            section_data,
            display_fields,
            self,
            allowed_ids=allowed_ids,
            store_field=store_field,
        )
        if dialog.exec() != QDialog.Accepted:
            return

        new_entity: dict[str, Any] | None = None
        if dialog.selected_index is not None:
            picked = section_data[dialog.selected_index]
            if isinstance(picked, dict):
                new_entity = picked

        _apply_roster_assignment(
            self.linked_context,
            org,
            self.roster_field,
            slot_index,
            new_entity,
            self.link_cfg,
            pick_from_org_field=self.pick_from_org_field,
        )
        roster = org.get(self.roster_field)
        self.set_slots_obj(roster if isinstance(roster, dict) else {})
        self.refresh()
        if self.on_roster_changed is not None:
            self.on_roster_changed()


class SectionEditorTab(QWidget):
    def __init__(
        self,
        section_key: str,
        section_file: Path,
        config: dict[str, Any],
        lang: str,
        linked_context: LinkedSectionContext | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.section_key = section_key
        self.section_file = section_file
        self.config = config
        self.lang = lang
        self.linked_context = linked_context
        self.alias_to_field = _alias_to_field_map(section_key)
        if linked_context is not None and section_key in linked_context.linked_config.managed_sections:
            self.section_data = linked_context.get_section(section_key)
            self.section_is_mapping = False
        else:
            raw_section = _load_json(section_file)
            self.section_is_mapping = isinstance(raw_section, dict)
            if isinstance(raw_section, list):
                self.section_data = raw_section
            elif isinstance(raw_section, dict):
                self.section_data = []
                for entry_key, entry_value in raw_section.items():
                    if isinstance(entry_value, dict):
                        row = dict(entry_value)
                    else:
                        row = {"__raw_value": entry_value}
                    row["__entry_key"] = str(entry_key)
                    self.section_data.append(row)
            else:
                self.section_data = []
        self.widgets: dict[str, Any] = {}
        self.skill_widgets: list[tuple[str, SkillEditorWidget]] = []
        self.roster_widgets: list[LinkedSlotsWidget] = []
        self.record_entries: list[tuple[int, str, str]] = []
        self.current_data_index: int | None = None

        root = QVBoxLayout(self)
        top = QVBoxLayout()
        search_row = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(I18N[self.lang]["record_search"])
        self.search_edit.textChanged.connect(self._filter_records)
        self.search_count_label = QLabel()
        search_row.addWidget(QLabel(I18N[self.lang]["record"]))
        search_row.addWidget(self.search_edit, 1)
        top.addLayout(search_row)
        top.addWidget(self.search_count_label)

        combo_row = QHBoxLayout()
        self.record_combo = QComboBox()
        self.record_combo.setMaxVisibleItems(20)
        self.record_combo.currentIndexChanged.connect(self._on_record_changed)
        combo_row.addWidget(self.record_combo, 1)
        top.addLayout(combo_row)
        root.addLayout(top)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        self.form = QFormLayout(inner)
        self.form.setLabelAlignment(Qt.AlignLeft)
        self.form.setFormAlignment(Qt.AlignTop)
        scroll.setWidget(inner)
        root.addWidget(scroll, 1)

        self._build_form()
        self._fill_record_combo()
        if self.record_combo.count() > 0:
            self._on_record_changed(0)

    def _display_label(self, item: dict[str, Any], fallback_idx: int | str) -> str:
        name_data = item.get("name", {})
        return (
            name_data.get(self.lang)
            or name_data.get("ru")
            or name_data.get("en")
            or I18N[self.lang]["property"].format(idx=fallback_idx)
        )

    def _resolve_object_key(self, item: dict[str, Any], idx: int) -> str:
        key = item.get("key")
        if isinstance(key, str) and key:
            return key
        alias = item.get("alias")
        if isinstance(alias, str) and alias:
            return alias
        return f"field_{idx}"

    def _build_object_editor(self, box: QGroupBox, field_defs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        box_layout = QFormLayout(box)
        nested_widgets: list[dict[str, Any]] = []
        for idx, sub in enumerate(field_defs):
            sub_type = str(sub.get("type", "text"))
            sub_key = self._resolve_object_key(sub, idx)
            sub_label = self._display_label(sub, sub_key)
            widget_info: dict[str, Any] = {"key": sub_key, "type": sub_type}
            if sub_type == "text":
                widget = QLineEdit()
            elif sub_type == "number":
                widget = QLineEdit()
                widget.setValidator(QDoubleValidator())
            elif sub_type == "checkbox":
                widget = QCheckBox()
            elif sub_type == "datetime":
                widget = QDateTimeEdit()
                widget.setCalendarPopup(True)
                widget.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
            else:
                # Fallback to text for unsupported nested types.
                widget = QLineEdit()
                widget_info["type"] = "text"
            box_layout.addRow(sub_label, widget)
            widget_info["widget"] = widget
            nested_widgets.append(widget_info)
        return nested_widgets

    def _set_basic_widget_value(self, field_type: str, widget: Any, value: Any) -> None:
        if field_type == "text":
            widget.setText(structured_value_to_text(value))
        elif field_type == "number":
            widget.setText("" if value is None else str(value))
        elif field_type == "checkbox":
            widget.setChecked(bool(value))
        elif field_type == "datetime":
            if isinstance(value, dict):
                iso = _timestamp_to_qdatetime_data(value) 
                try:
                    dt = datetime.fromisoformat(iso)
                    widget.setDateTime(dt.replace(tzinfo=None))
                except ValueError:
                    pass

    def _get_basic_widget_value(self, field_type: str, widget: Any, current_value: Any) -> Any:
        if field_type == "text":
            return text_to_structured_value(widget.text(), current_value)
        if field_type == "number":
            text = widget.text().strip()
            if not text:
                return current_value
            return float(text) if "." in text else int(text)
        if field_type == "checkbox":
            return widget.isChecked()
        if field_type == "datetime":
            dt = widget.dateTime().toPython()
            if isinstance(dt, datetime):
                return _qdatetime_to_timestamp_dict(dt.replace(tzinfo=timezone.utc))
            return current_value
        return current_value

    def _set_linked_slots(self, field_name: str, value: dict[str, Any]) -> None:
        row = self._current_record()
        if row is not None:
            row[field_name] = value

    def _refresh_all_roster_widgets(self) -> None:
        for roster_widget in self.roster_widgets:
            roster_widget.refresh()

    def _build_form(self) -> None:
        inputs = self.config.get("input", [])
        for i, item in enumerate(inputs, start=1):
            alias = item.get("alias", f"field_{i}")
            field_name = self.alias_to_field.get(alias, f"field_{i-1}")
            label = self._display_label(item, i)
            field_type = item.get("type", "text")

            if field_type == "text":
                widget = QLineEdit()
                self.form.addRow(label, widget)
                self.widgets[field_name] = ("text", widget)
            elif field_type == "number":
                widget = QLineEdit()
                widget.setValidator(QDoubleValidator())
                self.form.addRow(label, widget)
                self.widgets[field_name] = ("number", widget)
            elif field_type == "checkbox":
                widget = QCheckBox()
                self.form.addRow(label, widget)
                self.widgets[field_name] = ("checkbox", widget)
            elif field_type == "datetime":
                widget = QDateTimeEdit()
                widget.setCalendarPopup(True)
                widget.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
                self.form.addRow(label, widget)
                self.widgets[field_name] = ("datetime", widget)
            elif field_type == "skill_editor":
                options = item.get("options", [])
                box = QGroupBox(label)
                box_layout = QVBoxLayout(box)
                self.form.addRow(box)
                self.widgets[field_name] = ("skill_editor", box)
                for opt in options:
                    key = str(opt.get("key", "0"))
                    opt_name_data = opt.get("name", {})
                    name = (
                        opt_name_data.get(self.lang)
                        or opt_name_data.get("ru")
                        or opt_name_data.get("en")
                        or I18N[self.lang]["property"].format(idx=key)
                    )
                    skill_widget = SkillEditorWidget(name, self.lang)
                    box_layout.addWidget(skill_widget)
                    self.skill_widgets.append((key, skill_widget))
            elif field_type == "object":
                box = QGroupBox(label)
                nested_widgets = self._build_object_editor(box, item.get("fields", []))
                self.form.addRow(box)
                self.widgets[field_name] = ("object", {"box": box, "fields": nested_widgets})
            elif field_type == "linked_slots" and self.linked_context is not None:
                slot_count = int(item.get("slot_count", 0))
                link_cfg = item.get("link", {})
                pick_from_org_field = _resolve_pick_from_org_field(self.section_key, item)
                roster_widget = LinkedSlotsWidget(
                    self.lang,
                    slot_count,
                    link_cfg,
                    self.linked_context,
                    field_name,
                    lambda: self._current_record(),
                    lambda fn=field_name: (self._current_record() or {}).get(fn),
                    lambda value, fn=field_name: self._set_linked_slots(fn, value),
                    self._refresh_all_roster_widgets,
                    pick_from_org_field,
                    parent=self,
                )
                roster_widget.setTitle(label)
                self.form.addRow(roster_widget)
                self.widgets[field_name] = ("linked_slots", roster_widget)
                self.roster_widgets.append(roster_widget)
            else:
                widget = QLineEdit()
                self.form.addRow(label, widget)
                self.widgets[field_name] = ("text", widget)

    def _fill_record_combo(self) -> None:
        self.record_entries.clear()
        for idx, item in enumerate(self.section_data):
            label = _record_label(item, idx)
            blob = _record_search_blob(item, idx)
            self.record_entries.append((idx, label, blob))
        self._filter_records(self.search_edit.text())

    def _filter_records(self, query: str) -> None:
        needle = query.strip().lower()
        filtered = [
            entry
            for entry in self.record_entries
            if not needle or needle in entry[2] or needle in entry[1].lower()
        ]
        self.record_combo.blockSignals(True)
        self.record_combo.clear()
        for data_idx, label, _ in filtered:
            self.record_combo.addItem(label, data_idx)
        self.record_combo.blockSignals(False)
        self.search_count_label.setText(I18N[self.lang]["record_found"].format(count=len(filtered)))
        if self.record_combo.count() > 0:
            self._on_record_changed(0)
        else:
            self.current_data_index = None

    def _current_record(self) -> dict[str, Any] | None:
        if self.current_data_index is None:
            return None
        if self.current_data_index < 0 or self.current_data_index >= len(self.section_data):
            return None
        row = self.section_data[self.current_data_index] 
        return row if isinstance(row, dict) else None

    def _on_record_changed(self, combo_index: int) -> None:
        if combo_index < 0:
            return
        data_idx = self.record_combo.itemData(combo_index)
        if data_idx is None:
            return
        self.current_data_index = int(data_idx)
        row = self._current_record()
        if row is None:
            return
        for field_name, (field_type, widget) in self.widgets.items():
            value = row.get(field_name)
            if field_type in {"text", "number", "checkbox", "datetime"}:
                self._set_basic_widget_value(field_type, widget, value)
            elif field_type == "skill_editor":
                skill_root = value
                skill_map = None
                if isinstance(skill_root, list) and skill_root and isinstance(skill_root[0], dict):
                    skill_map = skill_root[0]
                for skill_key, skill_widget in self.skill_widgets:
                    skill_obj = None
                    if isinstance(skill_map, dict):
                        entries = skill_map.get(skill_key)
                        if isinstance(entries, list) and entries and isinstance(entries[0], dict):
                            skill_obj = entries[0]
                    skill_widget.bind_data(skill_obj)
            elif field_type == "object":
                obj_value = value if isinstance(value, dict) else {}
                for nested in widget.get("fields", []):
                    n_key = nested["key"]
                    n_type = nested["type"]
                    n_widget = nested["widget"]
                    self._set_basic_widget_value(n_type, n_widget, obj_value.get(n_key))
            elif field_type == "linked_slots":
                widget.refresh()

    def apply_changes(self) -> None:
        row = self._current_record()
        if row is None:
            return
        for field_name, (field_type, widget) in self.widgets.items():
            if field_type in {"text", "number", "checkbox", "datetime"}:
                row[field_name] = self._get_basic_widget_value(field_type, widget, row.get(field_name))
            elif field_type == "skill_editor":
                for _, skill_widget in self.skill_widgets:
                    skill_widget.apply_changes()
            elif field_type == "object":
                current_obj = row.get(field_name)
                obj = dict(current_obj) if isinstance(current_obj, dict) else {}
                for nested in widget.get("fields", []):
                    n_key = nested["key"]
                    n_type = nested["type"]
                    n_widget = nested["widget"]
                    obj[n_key] = self._get_basic_widget_value(n_type, n_widget, obj.get(n_key))
                row[field_name] = obj
        if self.section_is_mapping:
            out: dict[str, Any] = {}
            for item in self.section_data:
                if not isinstance(item, dict):
                    continue
                entry_key = str(item.get("__entry_key", ""))
                if not entry_key:
                    continue
                entry_value = {k: v for k, v in item.items() if k != "__entry_key"}
                out[entry_key] = entry_value
            _dump_json(self.section_file, out)
        else:
            _dump_json(self.section_file, self.section_data)


class SaveEditorWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.lang = "ru"
        self.app_cfg = _load_app_config()
        self.last_real_slot: str = str(self.app_cfg.get("selected_slot", "") or "")
        self.setWindowTitle(I18N[self.lang]["window_title"])
        self.resize(1220, 760) 

        self.loaded_ctx: dict[str, Path] | None = None
        self.linked_context: LinkedSectionContext | None = None
        self.section_tabs: list[SectionEditorTab] = []
        self.load_thread: QThread | None = None
        self.load_worker: LoadWorker | None = None
        self.save_thread: QThread | None = None
        self.save_worker: SaveWorker | None = None
        self.loading_overlay: LoadingOverlay | None = None

        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        lang_row = QHBoxLayout()
        self.lang_label = QLabel()
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("RU", "ru")
        self.lang_combo.addItem("EN", "en")
        self.lang_combo.currentIndexChanged.connect(self._on_language_changed)
        lang_row.addWidget(self.lang_label)
        lang_row.addWidget(self.lang_combo)
        lang_row.addStretch(1)
        layout.addLayout(lang_row)

        save_row = QHBoxLayout()
        self.save_path_edit = QLineEdit(str(self.app_cfg.get("save_path", DEFAULT_SAVE_ROOT)))
        self.save_browse_btn = QPushButton()
        self.save_browse_btn.clicked.connect(self._pick_save_dir)
        self.save_path_label = QLabel()
        save_row.addWidget(self.save_path_label)
        save_row.addWidget(self.save_path_edit, 1)
        save_row.addWidget(self.save_browse_btn)
        layout.addLayout(save_row)

        row3 = QHBoxLayout()
        self.slot_combo = QComboBox()
        self.slot_combo.currentIndexChanged.connect(self._on_slot_changed)
        self.refresh_slots_btn = QPushButton()
        self.refresh_slots_btn.clicked.connect(self._refresh_slots)
        self.load_btn = QPushButton()
        self.load_btn.clicked.connect(self._load_selected_slot)
        self.save_btn = QPushButton()
        self.save_btn.clicked.connect(self._save_to_mpack)
        self.slot_label = QLabel()
        row3.addWidget(self.slot_label)
        row3.addWidget(self.slot_combo, 1)
        row3.addWidget(self.refresh_slots_btn)
        row3.addWidget(self.load_btn)
        row3.addWidget(self.save_btn)
        layout.addLayout(row3)

        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs, 1)

        self._apply_language_texts()
        self._refresh_slots()

    def _tr(self, key: str, **kwargs: Any) -> str:
        return I18N[self.lang][key].format(**kwargs)

    def _apply_language_texts(self) -> None:
        self.setWindowTitle(self._tr("window_title"))
        self.lang_label.setText(self._tr("lang_label"))
        self.save_path_label.setText(self._tr("save_path"))
        self.slot_label.setText(self._tr("slot"))
        self.save_browse_btn.setText(self._tr("browse_save"))
        self.refresh_slots_btn.setText(self._tr("refresh_slots"))
        self.load_btn.setText(self._tr("load"))
        self.save_btn.setText(self._tr("save_mpack"))
        if not self.status_label.text().strip():
            self.status_label.setText(self._tr("status_wait"))

    def _on_language_changed(self) -> None:
        self.lang = self.lang_combo.currentData() or "ru"
        self._apply_language_texts()
        if self.loaded_ctx is not None:
            self._build_editor_tabs(self.loaded_ctx["sections_dir"])

    def _pick_save_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(self, self._tr("pick_save_title"), self.save_path_edit.text())
        if path:
            self.save_path_edit.setText(path)
            self.app_cfg["save_path"] = path
            _save_app_config(self.app_cfg)
            self._refresh_slots()

    def _refresh_slots(self) -> None:
        previous_slot = self.last_real_slot
        self.slot_combo.blockSignals(True)
        self.slot_combo.clear()
        save_root = Path(self.save_path_edit.text().strip())
        self.app_cfg["save_path"] = str(save_root)
        _save_app_config(self.app_cfg)
        if not save_root.exists():
            self.status_label.setText(self._tr("status_save_missing"))
            self.slot_combo.blockSignals(False)
            return
        real_slot_count = 0
        for file_path in find_slotdata_files(save_root):
            slot_id = file_path.parent.name
            self.slot_combo.addItem(slot_id, slot_id)
            real_slot_count += 1
        self.slot_combo.addItem(self._tr("slot_archive"), "__archive__")
        target_slot = str(self.app_cfg.get("selected_slot", "") or previous_slot or "")
        if target_slot:
            idx = self.slot_combo.findData(target_slot)
            if idx >= 0:
                self.slot_combo.setCurrentIndex(idx)
        if real_slot_count == 0:
            self.status_label.setText(self._tr("status_no_slots"))
        else:
            self.status_label.setText(self._tr("status_slots_found", count=real_slot_count))
        self.slot_combo.blockSignals(False)
        self._on_slot_changed(self.slot_combo.currentIndex())

    def _on_slot_changed(self, _: int) -> None:
        selected = self.slot_combo.currentData()
        if selected is None:
            return
        if selected != "__archive__":
            self.last_real_slot = str(selected)
            self.app_cfg["selected_slot"] = self.last_real_slot
            _save_app_config(self.app_cfg)

    def _clear_tabs(self) -> None:
        self.section_tabs.clear()
        while self.tabs.count() > 0:
            self.tabs.removeTab(0)

    def _set_busy(self, busy: bool) -> None:
        for widget in (
            self.save_path_edit,
            self.save_browse_btn,
            self.slot_combo,
            self.refresh_slots_btn,
            self.load_btn,
            self.save_btn,
            self.lang_combo,
        ):
            widget.setEnabled(not busy)

    def _show_loading(self, message: str) -> None:
        central = self.centralWidget()
        if central is None:
            return
        if self.loading_overlay is None:
            self.loading_overlay = LoadingOverlay(central, message)
        else:
            self.loading_overlay.set_message(message)
        self.loading_overlay.setGeometry(central.rect())
        self.loading_overlay.show()
        self.loading_overlay.raise_()

    def _hide_loading(self) -> None:
        if self.loading_overlay is not None:
            self.loading_overlay.hide()

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        if self.loading_overlay is not None and self.loading_overlay.isVisible():
            central = self.centralWidget()
            if central is not None:
                self.loading_overlay.setGeometry(central.rect())
        super().resizeEvent(event)

    def _cleanup_load_thread(self) -> None:
        if self.load_worker is not None:
            self.load_worker.deleteLater()
            self.load_worker = None
        if self.load_thread is not None:
            self.load_thread.deleteLater()
            self.load_thread = None

    def _cleanup_save_thread(self) -> None:
        if self.save_worker is not None:
            self.save_worker.deleteLater()
            self.save_worker = None
        if self.save_thread is not None:
            self.save_thread.deleteLater()
            self.save_thread = None

    def _load_selected_slot(self) -> None:
        save_root = Path(self.save_path_edit.text().strip())
        self.app_cfg["save_path"] = str(save_root)
        _save_app_config(self.app_cfg)
        selected = self.slot_combo.currentData()
        use_existing_workdir = selected == "__archive__"
        slot_id = self.last_real_slot if use_existing_workdir else str(selected or "").strip()
        if not slot_id:
            QMessageBox.warning(self, self._tr("no_slot_title"), self._tr("no_slot_text"))
            return
        if self.load_thread is not None and self.load_thread.isRunning():
            return

        self._set_busy(True)
        self.status_label.setText(self._tr("status_loading"))
        self._show_loading(self._tr("status_loading"))

        self.load_thread = QThread(self)
        self.load_worker = LoadWorker(save_root, slot_id, DEFAULT_WORK_ROOT, use_existing_workdir=use_existing_workdir)
        self.load_worker.moveToThread(self.load_thread)
        self.load_thread.started.connect(self.load_worker.run)
        self.load_worker.finished.connect(self._on_load_finished)
        self.load_worker.failed.connect(self._on_load_failed)
        self.load_worker.finished.connect(self.load_thread.quit)
        self.load_worker.failed.connect(self.load_thread.quit)
        self.load_thread.finished.connect(self._cleanup_load_thread)
        self.load_thread.start()

    def _on_load_finished(self, ctx: dict[str, Path]) -> None:
        slot_id = self.last_real_slot
        self.loaded_ctx = ctx
        self._build_editor_tabs(ctx["sections_dir"])
        self._hide_loading()
        self._set_busy(False)
        if bool(ctx.get("loaded_from_workdir")):
            self.status_label.setText(self._tr("status_workdir_loaded", slot=slot_id))
        else:
            self.status_label.setText(self._tr("status_loaded", slot=slot_id))

    def _on_load_failed(self, message: str) -> None:
        self._hide_loading()
        self._set_busy(False)
        self.status_label.setText(message)
        QMessageBox.critical(self, self._tr("load_error_title"), message)

    def _build_editor_tabs(self, sections_dir: Path) -> None:
        self._clear_tabs()
        self.linked_context = LinkedSectionContext(sections_dir, get_editor_linked_config())
        cfg = _load_json(EDITOR_CONFIG_PATH)
        for section_cfg in cfg:
            section_key = str(section_cfg.get("key"))
            section_file = sections_dir / f"section_{section_key}.json"
            if not section_file.exists():
                continue
            tab = SectionEditorTab(
                section_key,
                section_file,
                section_cfg,
                self.lang,
                linked_context=self.linked_context,
            )
            name_data = section_cfg.get("name", {})
            section_name = name_data.get(self.lang) or name_data.get("ru") or name_data.get("en") or section_cfg.get("code", section_key)
            self.tabs.addTab(tab, section_name)
            self.section_tabs.append(tab)

    def _save_to_mpack(self) -> None:
        if self.loaded_ctx is None:
            QMessageBox.warning(self, self._tr("no_data_title"), self._tr("no_data_text"))
            return
        if self.save_thread is not None and self.save_thread.isRunning():
            return

        self._set_busy(True)
        self._show_loading(self._tr("saving_title"))
        for tab in self.section_tabs:
            tab.apply_changes()
        if self.linked_context is not None:
            self.linked_context.save_managed_sections()

        managed_section_keys = list(get_editor_linked_config().managed_sections)
        self.save_thread = QThread(self)
        self.save_worker = SaveWorker(self.loaded_ctx, managed_section_keys)
        self.save_worker.moveToThread(self.save_thread)
        self.save_thread.started.connect(self.save_worker.run)
        self.save_worker.finished.connect(self._on_save_finished)
        self.save_worker.failed.connect(self._on_save_failed)
        self.save_worker.finished.connect(self.save_thread.quit)
        self.save_worker.failed.connect(self.save_thread.quit)
        self.save_thread.finished.connect(self._cleanup_save_thread)
        self.save_thread.start()

    def _on_save_finished(self, source_mpack: str) -> None:
        backup_path = Path(source_mpack).with_suffix(".mpack.bak")
        if self.loaded_ctx is not None:
            try:
                self.loaded_ctx["base_mpack_bytes"] = Path(source_mpack).read_bytes()
            except OSError:
                pass
        self._hide_loading()
        self._set_busy(False)
        self.status_label.setText(self._tr("status_saved", path=source_mpack))
        QMessageBox.information(
            self,
            self._tr("success_title"),
            self._tr("success_text", path=source_mpack, backup=backup_path),
        )

    def _on_save_failed(self, message: str) -> None:
        self._hide_loading()
        self._set_busy(False)
        QMessageBox.critical(self, self._tr("save_error_title"), message)


def main() -> None:
    app = QApplication(sys.argv)
    win = SaveEditorWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

from __future__ import annotations

import ast
import base64
import json
import re
import shutil
from datetime import timezone
from pathlib import Path
from typing import Any

import msgpack

TIMESTAMP_KEYS = {"__timestamp_iso_utc__", "__timestamp_seconds__", "__timestamp_nanoseconds__"}
BYTES_KEY = "__bytes_base64__"


def json_safe(value: Any) -> Any:
    if isinstance(value, msgpack.Timestamp):
        dt = value.to_datetime().astimezone(timezone.utc)
        return {
            "__timestamp_iso_utc__": dt.isoformat().replace("+00:00", "Z"),
            "__timestamp_seconds__": value.seconds,
            "__timestamp_nanoseconds__": value.nanoseconds, 
        }
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for k, v in value.items():
            if isinstance(k, bytes):
                key = k.decode("utf-8", errors="replace")
            else:
                key = str(k)
            out[key] = json_safe(v)
        return out
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    if isinstance(value, set):
        return [json_safe(item) for item in sorted(value, key=lambda x: str(x))]
    if isinstance(value, bytes):
        try:
            return value.decode("utf-8")
        except UnicodeDecodeError:
            return {BYTES_KEY: base64.b64encode(value).decode("ascii")}
    return value


def is_timestamp_obj(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    if TIMESTAMP_KEYS.issubset(value.keys()):
        return True
    return "__timestamp_unix__" in value


def _is_numeric_key(key: str) -> bool:
    return key.isdigit() or (key.startswith("-") and key[1:].isdigit())


def _should_restore_int_keys(data: dict[str, Any]) -> bool:
    if not data:
        return False
    if not all(isinstance(k, str) and _is_numeric_key(k) for k in data): 
        return False
    ints = sorted(int(k) for k in data)
    return ints == list(range(len(ints)))


def _is_field_key(key: str) -> bool: 
    return key.startswith("field_") and key[6:].isdigit()


def _should_restore_field_list(data: dict[str, Any]) -> bool:
    if not data:
        return False
    if not all(isinstance(k, str) and _is_field_key(k) for k in data):
        return False
    indexes = sorted(int(k[6:]) for k in data)
    return indexes == list(range(len(indexes)))


def _restore_dict_keys(data: dict[str, Any]) -> dict[Any, Any]:
    if _should_restore_int_keys(data):
        return {int(k): msgpack_safe(v) for k, v in data.items()}
    return {k: msgpack_safe(v) for k, v in data.items()}


def msgpack_safe(value: Any) -> Any:
    if is_timestamp_obj(value):
        if TIMESTAMP_KEYS.issubset(value.keys()):
            return msgpack.Timestamp(
                int(value["__timestamp_seconds__"]),
                int(value["__timestamp_nanoseconds__"]),
            )
        return msgpack.Timestamp.from_unix(float(value["__timestamp_unix__"]))
    if isinstance(value, dict):
        if len(value) == 1 and BYTES_KEY in value:
            return base64.b64decode(value[BYTES_KEY])
        if _should_restore_field_list(value):
            out: list[Any] = []
            for idx in range(len(value)):
                out.append(msgpack_safe(value[f"field_{idx}"]))
            return out
        return _restore_dict_keys(value)
    if isinstance(value, list):
        return [msgpack_safe(item) for item in value]
    return value


def unpack_bytes(data: bytes) -> Any:
    return msgpack.unpackb(data, raw=False, strict_map_key=False)


def pack_value(value: Any) -> bytes:
    return msgpack.packb(msgpack_safe(value), use_bin_type=True)


def unpack_file_to_json(source: Path, output: Path, *, indent: int = 2) -> None:
    raw = source.read_bytes()
    unpacked = unpack_bytes(raw)
    safe = json_safe(unpacked)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(safe, ensure_ascii=False, indent=indent),
        encoding="utf-8",
    )


def pack_json_to_file(source: Path, output: Path) -> None:
    loaded = json.loads(source.read_text(encoding="utf-8"))
    packed = pack_value(loaded)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(packed)


def unpack_tree(root: Path, out_root: Path) -> list[tuple[Path, Path, str | None]]:
    results: list[tuple[Path, Path, str | None]] = []
    for source in sorted(root.rglob("*.mpack")):
        rel = source.relative_to(root)
        output = out_root / rel.with_suffix(".json")
        try:
            unpack_file_to_json(source, output)
            results.append((source, output, None))
        except Exception as exc:
            results.append((source, output, str(exc)))
    return results


def pack_tree(root: Path, out_root: Path) -> list[tuple[Path, Path, str | None]]:
    results: list[tuple[Path, Path, str | None]] = []
    for source in sorted(root.rglob("*.json")):
        rel = source.relative_to(root)
        output = out_root / rel.with_suffix(".mpack")
        try:
            pack_json_to_file(source, output)
            results.append((source, output, None))
        except Exception as exc:
            results.append((source, output, str(exc)))
    return results


def _looks_like_struct_list(value: list[Any]) -> bool:
    # Heuristic: list with multiple primitive-like positions is likely a serialized C# object.
    if len(value) < 2:
        return False
    primitive_count = sum(isinstance(item, (str, int, float, bool)) or item is None for item in value)
    return primitive_count >= max(1, len(value) // 2)


def readable_view(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): readable_view(v) for k, v in value.items()}
    if isinstance(value, list):
        if _looks_like_struct_list(value):
            return {f"field_{idx}": readable_view(item) for idx, item in enumerate(value)}
        return [readable_view(item) for item in value]
    return value


def unpack_file_to_readable_json(source: Path, output: Path, *, indent: int = 2) -> None:
    raw = source.read_bytes()
    unpacked = unpack_bytes(raw)
    safe = json_safe(unpacked)
    readable = readable_view(safe)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(readable, ensure_ascii=False, indent=indent),
        encoding="utf-8",
    )


def unpack_tree_readable(root: Path, out_root: Path) -> list[tuple[Path, Path, str | None]]:
    results: list[tuple[Path, Path, str | None]] = []
    for source in sorted(root.rglob("*.mpack")):
        rel = source.relative_to(root)
        output = out_root / rel.with_suffix(".json")
        try:
            unpack_file_to_readable_json(source, output)
            results.append((source, output, None))
        except Exception as exc:
            results.append((source, output, str(exc)))
    return results


def find_slotdata_files(save_root: Path) -> list[Path]:
    results: list[Path] = []
    if not save_root.exists():
        return results
    for child in sorted(save_root.iterdir()):
        if not child.is_dir() or not child.name.isdigit():
            continue
        candidate = child / "SlotData.mpack"
        if candidate.exists():
            results.append(candidate)
    return results


def unpack_slotdata_readable(
    save_root: Path,
    output_root: Path,
    *,
    indent: int = 2,
) -> list[tuple[Path, Path, str | None]]:
    results: list[tuple[Path, Path, str | None]] = []
    slot_files = find_slotdata_files(save_root)
    for source in slot_files:
        slot_id = source.parent.name
        output = output_root / slot_id / "SlotData.readable.json"
        try:
            unpack_file_to_readable_json(source, output, indent=indent)
            results.append((source, output, None))
        except Exception as exc:
            results.append((source, output, str(exc)))
    return results


def _safe_name(text: str, max_len: int = 80) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("._")
    if not cleaned:
        cleaned = "item"
    return cleaned[:max_len]


def _load_section_profile(profile_path: Path) -> dict[str, Any]:
    if not profile_path.exists():
        return {"section_titles": {}, "field_aliases": {}}
    try:
        raw = json.loads(profile_path.read_text(encoding="utf-8"))
    except Exception:
        return {"section_titles": {}, "field_aliases": {}}
    return {
        "section_titles": raw.get("section_titles", {}) or {},
        "field_aliases": raw.get("field_aliases", {}) or {},
    }


def split_top_level_sections(
    source_json: Path,
    output_dir: Path,
    *,
    profile_path: Path | None = None,
    indent: int = 2,
) -> tuple[int, Path]:
    data = json.loads(source_json.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    default_profile = Path(__file__).resolve().parent / "section_profile.json"
    profile = _load_section_profile(profile_path or default_profile)
    section_titles: dict[str, str] = profile.get("section_titles", {})
    field_aliases: dict[str, Any] = profile.get("field_aliases", {})

    manifest: dict[str, Any] = {
        "source": str(source_json),
        "root_type": type(data).__name__,
        "profile": str((profile_path or default_profile).resolve()),
        "field_aliases_sections": sorted(field_aliases.keys()),
        "sections": [],
    }

    if isinstance(data, list):
        for idx, item in enumerate(data, start=1):
            name = f"section_{idx}.json"
            target = output_dir / name
            target.write_text(json.dumps(item, ensure_ascii=False, indent=indent), encoding="utf-8")
            row = {
                "index": idx,
                "file": name,
                "type": type(item).__name__,
                "length": len(item) if hasattr(item, "__len__") else None,
            }
            title = section_titles.get(str(idx))
            if title:
                row["title"] = title
            manifest["sections"].append(row)
    elif isinstance(data, dict):
        for idx, (key, item) in enumerate(data.items(), start=1):
            key_name = _safe_name(str(key))
            name = f"section_{idx}_{key_name}.json"
            target = output_dir / name
            target.write_text(json.dumps(item, ensure_ascii=False, indent=indent), encoding="utf-8")
            row = {
                "index": idx,
                "key": str(key),
                "file": name,
                "type": type(item).__name__,
                "length": len(item) if hasattr(item, "__len__") else None,
            }
            title = section_titles.get(str(idx))
            if title:
                row["title"] = title
            manifest["sections"].append(row)
    else:
        name = "section_1.json"
        target = output_dir / name
        target.write_text(json.dumps(data, ensure_ascii=False, indent=indent), encoding="utf-8")
        row = {
            "index": 1,
            "file": name,
            "type": type(data).__name__,
            "length": len(data) if hasattr(data, "__len__") else None,
        }
        title = section_titles.get("1")
        if title:
            row["title"] = title
        manifest["sections"].append(row)

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=indent), encoding="utf-8")
    return len(manifest["sections"]), manifest_path


def _is_corrupted_readable_struct_text(text: str) -> bool:
    stripped = text.strip()
    if not stripped or stripped[0] not in "{[":
        return False
    # Only repair strings produced by GUI str(dict) corruption of readable_view data.
    return "field_" in stripped


def _try_parse_structured_text(text: str) -> Any | None:
    stripped = text.strip()
    if not stripped or stripped[0] not in "{[":
        return None
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        try:
            parsed = ast.literal_eval(stripped)
        except (ValueError, SyntaxError):
            return None
    if isinstance(parsed, (dict, list)):
        return parsed
    return None


def repair_readable_value(value: Any) -> Any:
    if isinstance(value, str):
        if not _is_corrupted_readable_struct_text(value):
            return value
        parsed = _try_parse_structured_text(value)
        return repair_readable_value(parsed) if parsed is not None else value
    if isinstance(value, dict):
        return {k: repair_readable_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [repair_readable_value(item) for item in value]
    return value


def structured_value_to_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, str) and _is_corrupted_readable_struct_text(value):
        parsed = _try_parse_structured_text(value)
        if parsed is not None:
            return json.dumps(parsed, ensure_ascii=False)
    return str(value)


def text_to_structured_value(text: str, original: Any = None) -> Any:
    if isinstance(original, (dict, list)):
        if not text.strip():
            return original
        parsed = _try_parse_structured_text(text)
        return parsed if parsed is not None else text
    if isinstance(original, str) and _is_corrupted_readable_struct_text(original):
        if not text.strip():
            return original
        parsed = _try_parse_structured_text(text)
        return parsed if parsed is not None else text
    return text
 

def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any, *, indent: int = 2) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=indent), encoding="utf-8")


def extract_slotdata_to_sections(
    save_root: Path,
    slot_id: str,
    work_root: Path,
    *,
    indent: int = 2,
    profile_path: Path | None = None,
) -> dict[str, Path]:
    source_mpack = save_root / slot_id / "SlotData.mpack" 
    if not source_mpack.exists():
        raise FileNotFoundError(f"SlotData.mpack not found: {source_mpack}")

    slot_work = work_root / slot_id
    if slot_work.exists():
        shutil.rmtree(slot_work)
    slot_work.mkdir(parents=True, exist_ok=True)
    readable_json = slot_work / "SlotData.readable.json"
    sections_dir = slot_work / "SlotData.readable_sections"

    unpack_file_to_readable_json(source_mpack, readable_json, indent=indent)
    _, manifest_path = split_top_level_sections(
        readable_json,
        sections_dir,
        profile_path=profile_path,
        indent=indent,
    )
    return {
        "source_mpack": source_mpack,
        "slot_work": slot_work,
        "readable_json": readable_json,
        "sections_dir": sections_dir,
        "manifest": manifest_path,
    }


def assemble_root_from_sections(sections_dir: Path) -> Any:
    manifest_path = sections_dir / "manifest.json"
    manifest = _read_json(manifest_path)
    root_type = manifest.get("root_type")
    rows: list[dict[str, Any]] = manifest.get("sections", [])
    if root_type == "list":
        items: list[Any] = []
        for row in sorted(rows, key=lambda r: int(r.get("index", 0))):
            items.append(repair_readable_value(_read_json(sections_dir / row["file"])))
        return items
    if root_type == "dict":
        out: dict[str, Any] = {}
        for row in sorted(rows, key=lambda r: int(r.get("index", 0))):
            key = row.get("key")
            if key is None:
                key = row.get("file", f"section_{row.get('index')}")
            out[str(key)] = repair_readable_value(_read_json(sections_dir / row["file"]))
        return out
    if rows:
        return repair_readable_value(_read_json(sections_dir / rows[0]["file"]))
    return None


def pack_sections_to_slotdata(
    sections_dir: Path,
    output_mpack: Path,
    *,
    output_readable_json: Path | None = None,
    indent: int = 2,
) -> Path:
    root_value = assemble_root_from_sections(sections_dir)
    if output_readable_json is not None:
        _write_json(output_readable_json, root_value, indent=indent)
    output_mpack.parent.mkdir(parents=True, exist_ok=True)
    output_mpack.write_bytes(pack_value(root_value))
    return output_mpack


def pack_slotdata_with_section_overrides(
    base_mpack: Path | bytes,
    sections_dir: Path,
    output_mpack: Path,
    section_keys: list[str],
    *,
    output_readable_json: Path | None = None,
    indent: int = 2,
) -> Path:
    base_bytes = base_mpack.read_bytes() if isinstance(base_mpack, Path) else base_mpack
    root_value = unpack_bytes(base_bytes)
    manifest = _read_json(sections_dir / "manifest.json")
    root_type = manifest.get("root_type")
    if root_type != "list" or not isinstance(root_value, list):
        raise ValueError("Section overrides are supported only for list-root SlotData saves.")

    for section_key in section_keys:
        section_path = sections_dir / f"section_{section_key}.json"
        if not section_path.exists():
            continue
        index = int(section_key) - 1
        if index < 0 or index >= len(root_value):
            raise IndexError(f"Section {section_key} is out of range for SlotData root list.")
        root_value[index] = repair_readable_value(_read_json(section_path))

    packed = pack_value(root_value)
    output_mpack.parent.mkdir(parents=True, exist_ok=True)
    output_mpack.write_bytes(packed)
    if output_readable_json is not None:
        readable = readable_view(json_safe(unpack_bytes(packed)))
        _write_json(output_readable_json, readable, indent=indent)
    return output_mpack

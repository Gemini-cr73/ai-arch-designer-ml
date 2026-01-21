from __future__ import annotations

import io
import zipfile


def build_scaffold_zip_bytes(files: dict[str, str]) -> bytes:
    """
    Build an in-memory ZIP from scaffold `files` map: path -> content.
    Paths should already be normalized (forward slashes, no traversal).
    """
    buf = io.BytesIO()

    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path, content in files.items():
            # Safety: block absolute paths or traversal (defense in depth)
            safe_path = (path or "").replace("\\", "/").lstrip("/")
            if ".." in safe_path.split("/"):
                continue  # skip anything suspicious

            zf.writestr(safe_path, content or "")

    buf.seek(0)
    return buf.getvalue()

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict
import threading
from concurrent.futures import ThreadPoolExecutor
import time

import rawpy
from PIL import Image

# Common RAW extensions
RAW_EXTS = {".cr3", ".cr2", ".dng", ".nef", ".arw", ".raf", ".rw2", ".orf", ".srw"}


@dataclass
class PreviewsOptions:
    size_mode: str = "exact_224"            # "exact_224" | "short256_center224" | "none"
    fmt: str = "jpeg"                       # "jpeg" | "webp"
    quality: int = 88                       # 60..95
    recursive: bool = True
    overwrite: bool = False
    max_workers: int = 4
    limit: Optional[int] = None


@dataclass
class PreviewsJob:
    source_dir: Path
    out_dir: Path
    options: PreviewsOptions
    total: int = 0
    completed: int = 0
    skipped: int = 0
    failed: int = 0
    started_at: float = field(default_factory=time.time)
    finished_at: Optional[float] = None
    status: str = "pending"                 # "pending" | "running" | "done" | "cancelled"
    cancelled: bool = False
    lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    _executor: Optional[ThreadPoolExecutor] = field(default=None, init=False, repr=False)
    logs: List[Dict] = field(default_factory=list)  # recent per-file results

    def start(self):
        """Fire-and-forget start of conversion workers."""
        self.status = "running"
        self.out_dir.mkdir(parents=True, exist_ok=True)
        files = list(enumerate_raw_files(self.source_dir, self.options.recursive))
        if self.options.limit:
            files = files[: int(self.options.limit)]
        self.total = len(files)
        if self.total == 0:
            self.status = "done"
            self.finished_at = time.time()
            return

        self._executor = ThreadPoolExecutor(max_workers=self.options.max_workers)
        for p in files:
            self._executor.submit(self._worker, p)

        # Monitor on a background thread so start() returns immediately
        threading.Thread(target=self._wait_for_completion, daemon=True).start()

    def _wait_for_completion(self):
        while True:
            with self.lock:
                done = (self.completed + self.skipped + self.failed) >= self.total or self.cancelled
            if done:
                break
            time.sleep(0.25)

        if self._executor:
            self._executor.shutdown(wait=True, cancel_futures=True)

        with self.lock:
            self.status = "cancelled" if self.cancelled else "done"
            self.finished_at = time.time()

    def cancel(self):
        with self.lock:
            self.cancelled = True

    def progress(self) -> float:
        with self.lock:
            if self.total == 0:
                return 0.0
            return min(1.0, (self.completed + self.skipped + self.failed) / self.total)

    def _worker(self, raw_path: Path):
        if self.cancelled:
            return
        try:
            out_path = self._map_out_path(raw_path)
            if not self.options.overwrite and out_path.exists():
                with self.lock:
                    self.skipped += 1
                    self.logs.append({"raw": str(raw_path), "out": str(out_path), "status": "skipped"})
                return

            img = raw_to_image(raw_path)
            img = apply_resize(img, self.options.size_mode)
            save_image(img, out_path, self.options.fmt, self.options.quality)

            with self.lock:
                self.completed += 1
                self.logs.append({"raw": str(raw_path), "out": str(out_path), "status": "ok"})
        except Exception as e:
            with self.lock:
                self.failed += 1
                self.logs.append({"raw": str(raw_path), "out": "", "status": "fail", "error": str(e)})

    def _map_out_path(self, raw_path: Path) -> Path:
        ext = ".webp" if self.options.fmt.lower() == "webp" else ".jpg"
        return self.out_dir / f"{raw_path.stem}{ext}"


# Global in-memory job registry (persists across browser refreshes while the server runs)
_JOBS: List[PreviewsJob] = []

def _register_job(job: PreviewsJob) -> None:
    _JOBS.append(job)

def find_active_job(source_dir: Optional[Path] = None, out_dir: Optional[Path] = None) -> Optional[PreviewsJob]:
    """
    Try to reclaim an active job by matching source/out dirs. If both are None, returns the most recent active job.
    """
    candidates = [j for j in _JOBS if j.status in ("pending", "running") and not j.cancelled]
    if out_dir:
        out_dir = Path(out_dir).resolve()
        candidates = [j for j in candidates if j.out_dir.resolve() == out_dir]
    if source_dir:
        source_dir = Path(source_dir).resolve()
        candidates = [j for j in candidates if j.source_dir.resolve() == source_dir]
    candidates.sort(key=lambda j: j.started_at, reverse=True)
    return candidates[0] if candidates else None


def enumerate_raw_files(src: Path, recursive: bool) -> List[Path]:
    if not src.exists():
        return []
    patterns = ["**/*"] if recursive else ["*"]
    out: List[Path] = []
    for pat in patterns:
        for p in src.glob(pat):
            if p.is_file() and p.suffix.lower() in RAW_EXTS:
                out.append(p)
    out.sort()
    return out


def raw_to_image(raw_path: Path) -> Image.Image:
    """Convert a RAW file to a PIL RGB image using rawpy/LibRaw."""
    with rawpy.imread(str(raw_path)) as raw:
        rgb = raw.postprocess(
            use_camera_wb=True,
            no_auto_bright=True,
            output_bps=8,
            gamma=(2.222, 4.5),
            demosaic_algorithm=rawpy.DemosaicAlgorithm.AHD,
            bright=1.0,
        )
    img = Image.fromarray(rgb)
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img


def apply_resize(img: Image.Image, mode: str) -> Image.Image:
    """Apply the requested sizing mode."""
    mode = (mode or "").lower()
    if mode == "exact_224":
        return img.resize((224, 224), Image.BICUBIC)
    if mode == "short256_center224":
        w, h = img.size
        if min(w, h) == 0:
            return img
        scale = 256.0 / min(w, h)
        new_w = int(round(w * scale))
        new_h = int(round(h * scale))
        img = img.resize((new_w, new_h), Image.BICUBIC)
        left = max(0, (new_w - 224) // 2)
        top = max(0, (new_h - 224) // 2)
        return img.crop((left, top, left + 224, top + 224))
    # "none" or unknown -> keep original sizing
    return img


def save_image(img: Image.Image, out_path: Path, fmt: str, quality: int):
    fmt = (fmt or "jpeg").lower()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "webp":
        img.save(out_path, format="WEBP", quality=int(quality), method=6)
    else:
        img.save(out_path, format="JPEG", quality=int(quality), optimize=True, progressive=True)


def start_previews_job(
    source_dir: Path,
    out_dir: Path,
    *,
    size_mode: str = "exact_224",
    fmt: str = "jpeg",
    quality: int = 88,
    recursive: bool = True,
    overwrite: bool = False,
    max_workers: int = 4,
    limit: Optional[int] = None,
) -> PreviewsJob:
    job = PreviewsJob(
        source_dir=Path(source_dir),
        out_dir=Path(out_dir),
        options=PreviewsOptions(
            size_mode=size_mode,
            fmt=fmt,
            quality=quality,
            recursive=recursive,
            overwrite=overwrite,
            max_workers=max_workers,
            limit=limit,
        ),
    )
    _register_job(job)
    job.start()
    return job


def is_job_active(job: Optional[PreviewsJob]) -> bool:
    if job is None:
        return False
    return job.status in ("pending", "running") and not job.cancelled
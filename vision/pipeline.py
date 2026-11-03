from __future__ import annotations

import io
from decimal import Decimal
from pathlib import Path

from django.core.files.base import ContentFile
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFilter

from damages.models import DamageCatalog, DamageDetection, SeverityLevel
from reports.models import ReportStatus
from reports.services import transition_report
from vision.models import VisionJob, VisionJobStatus


def enqueue_vision_job(report) -> VisionJob:
    job = VisionJob.objects.create(report=report)
    transition_report(report, ReportStatus.PROCESSING, reason="Computer vision pipeline started")
    start_job_async(job.id)
    return job


def start_job_async(job_id) -> None:
    import threading

    thread = threading.Thread(target=run_vision_job, args=(str(job_id),), daemon=True)
    thread.start()


def run_vision_job(job_id: str) -> None:
    job = VisionJob.objects.select_related("report").get(pk=job_id)
    job.status = VisionJobStatus.RUNNING
    job.started_at = timezone.now()
    job.save(update_fields=["status", "started_at"])
    log_lines: list[str] = []
    try:
        report = job.report
        image = _load_report_image(report)
        log_lines.append(f"Loaded image {image.size[0]}x{image.size[1]}")

        blurred = image.convert("RGB")
        if job.blur_faces or job.blur_plates:
            blurred, blur_notes = _blur_sensitive_regions(blurred)
            log_lines.extend(blur_notes)

        detections = _detect_damages(blurred)
        log_lines.append(f"Model {job.model_name} returned {len(detections)} candidate(s)")

        annotated = blurred.copy()
        draw = ImageDraw.Draw(annotated)
        catalog_map = {c.damage_code: c for c in DamageCatalog.objects.all()}
        written = 0
        for det in detections:
            catalog = catalog_map.get(det["code"])
            if not catalog:
                continue
            bbox = det["bbox"]
            x1, y1, x2, y2 = bbox["x1"], bbox["y1"], bbox["x2"], bbox["y2"]
            draw.rectangle([x1, y1, x2, y2], outline="#E85D04", width=4)
            draw.text((x1 + 6, max(y1 - 16, 0)), det["code"], fill="#E85D04")
            DamageDetection.objects.create(
                report=report,
                catalog=catalog,
                confidence=Decimal(str(det["confidence"])),
                severity=det["severity"],
                raw_bbox=bbox,
                estimated_area_sqm=Decimal(str(det["area_sqm"])),
                estimated_depth_cm=Decimal(str(det["depth_cm"])),
            )
            written += 1

        buffer = io.BytesIO()
        annotated.save(buffer, format="JPEG", quality=88)
        filename = f"{report.id}-annotated.jpg"
        report.annotated_image.save(filename, ContentFile(buffer.getvalue()), save=False)
        report.annotated_image_url = report.annotated_image.url
        report.save(update_fields=["annotated_image", "annotated_image_url", "updated_at"])

        job.detections_written = written
        job.status = VisionJobStatus.COMPLETED
        job.finished_at = timezone.now()
        job.log = "\n".join(log_lines)
        job.save()
        transition_report(
            report,
            ReportStatus.PROCESSING,
            reason=f"CV completed with {written} detection(s); awaiting inspector review",
        )
    except Exception as exc:  # noqa: BLE001 — job must never crash the worker silently
        job.status = VisionJobStatus.FAILED
        job.finished_at = timezone.now()
        job.log = "\n".join(log_lines + [f"ERROR: {exc}"])
        job.save(update_fields=["status", "finished_at", "log"])


def _load_report_image(report) -> Image.Image:
    if report.original_image:
        # Close the file once it's read; an open handle keeps it locked on Windows,
        # so the report's photo couldn't be deleted afterwards.
        with report.original_image.open("rb") as image_file:
            return Image.open(image_file).copy()
    raise FileNotFoundError("Report has no original image to analyse")


def _blur_sensitive_regions(image: Image.Image) -> tuple[Image.Image, list[str]]:
    notes = ["Privacy pass: scanning for faces and license plates"]
    opencv_image = None
    try:
        import cv2
        import numpy as np

        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        cascade_dir = Path(cv2.data.haarcascades)
        face_cascade = cv2.CascadeClassifier(str(cascade_dir / "haarcascade_frontalface_default.xml"))
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)
        notes.append(f"Faces detected: {len(faces)}")
        for x, y, w, h in faces:
            image = _box_blur(image, x, y, x + w, y + h)

        plate_cascade_path = cascade_dir / "haarcascade_russian_plate_number.xml"
        if plate_cascade_path.exists():
            plates = cv2.CascadeClassifier(str(plate_cascade_path)).detectMultiScale(gray, 1.1, 5)
            notes.append(f"Plates detected: {len(plates)}")
            for x, y, w, h in plates:
                image = _box_blur(image, x, y, x + w, y + h)
        else:
            notes.append("Plate cascade not bundled; applied conservative lower-band blur")
            w, h = image.size
            image = _box_blur(image, 0, int(h * 0.72), w, h, radius=8)
    except Exception as exc:  # OpenCV optional
        notes.append(f"OpenCV unavailable ({exc}); applied conservative privacy blur")
        w, h = image.size
        image = _box_blur(image, 0, int(h * 0.08), w, int(h * 0.28), radius=12)
        image = _box_blur(image, 0, int(h * 0.72), w, h, radius=8)
    return image, notes


def _box_blur(image: Image.Image, x1: int, y1: int, x2: int, y2: int, radius: int = 18) -> Image.Image:
    x1, y1, x2, y2 = map(int, (max(x1, 0), max(y1, 0), x2, y2))
    region = image.crop((x1, y1, x2, y2)).filter(ImageFilter.GaussianBlur(radius))
    image.paste(region, (x1, y1))
    return image


def _detect_damages(image: Image.Image) -> list[dict]:
    """Lightweight stand-in for the production CV model.

    Dark, compact regions are treated as pothole candidates so the rest of
    the registry, BOQ and repair workflow can run without a GPU model.
    """
    # A black, white, blank or blurry photo has nothing to find; it must not look like a pothole.
    from reports.photo_quality import problem_with

    if problem_with(image):
        return []
    gray = image.convert("L")
    w, h = gray.size
    pixels = list(gray.getdata())
    threshold = 70
    dark = sum(1 for p in pixels if p < threshold)
    ratio = dark / max(len(pixels), 1)

    detections = []
    if ratio > 0.02:
        pad_x, pad_y = int(w * 0.28), int(h * 0.30)
        detections.append(
            {
                "code": "POTHOLE_DEEP" if ratio > 0.08 else "POTHOLE_SHALLOW",
                "confidence": round(min(0.97, 0.55 + ratio), 3),
                "severity": SeverityLevel.HIGH if ratio > 0.08 else SeverityLevel.MEDIUM,
                "bbox": {
                    "x1": pad_x,
                    "y1": pad_y,
                    "x2": w - pad_x,
                    "y2": h - pad_y,
                    "normalized": True,
                    "image_width": w,
                    "image_height": h,
                },
                "area_sqm": round(0.4 + ratio * 6, 3),
                "depth_cm": round(3 + ratio * 20, 2),
            }
        )
    if ratio > 0.12:
        detections.append(
            {
                "code": "CRACK_NETWORK",
                "confidence": 0.62,
                "severity": SeverityLevel.MEDIUM,
                "bbox": {
                    "x1": int(w * 0.12),
                    "y1": int(h * 0.18),
                    "x2": int(w * 0.88),
                    "y2": int(h * 0.42),
                    "image_width": w,
                    "image_height": h,
                },
                "area_sqm": 1.25,
                "depth_cm": 1.5,
            }
        )
    return detections

"""Prepare website PDFs for progressive loading without changing page layout.

Requires pymupdf, pikepdf, and Pillow. Vector restoration is optional and only
matches embedded images to pixel-identical PNGs from the paper's figure folder.
The matching vector PDF must have the same figure name without `_aaai27`.
"""

import argparse
import hashlib
import io
import json
from pathlib import Path

import pikepdf
import pymupdf
from PIL import Image


def pixel_hash(image):
    rgb = image.convert("RGB")
    return rgb.size, hashlib.sha256(rgb.tobytes()).hexdigest()


def optimize(source, destination, figures=None):
    originals = {}
    if figures:
        for png in figures.glob("*_aaai27.png"):
            vector = png.with_name(png.stem.replace("_aaai27", "") + ".pdf")
            if vector.is_file():
                with Image.open(png) as image:
                    originals[pixel_hash(image)] = vector

    restored = []
    with pymupdf.open(source) as document:
        owners = {}
        for page in document:
            for image in page.get_images(full=True):
                owners.setdefault(image[0], set()).add(page.number)
        for page in document:
            for image in page.get_images(full=True):
                xref = image[0]
                embedded = document.extract_image(xref)
                with Image.open(io.BytesIO(embedded["image"])) as raster:
                    vector = originals.get(pixel_hash(raster))
                if vector is None:
                    continue
                if len(owners[xref]) > 1:
                    raise ValueError("Shared figure xrefs require restoring all page placements first")
                rectangles = page.get_image_rects(xref)
                with pymupdf.open(vector) as figure:
                    for rectangle in rectangles:
                        # Remove only the matched raster; retain all surrounding
                        # text, captions, annotations, and page coordinates.
                        page.show_pdf_page(rectangle, figure, 0, keep_proportion=False)
                page.delete_image(xref)
                restored.append({"page": page.number + 1, "figure": vector.name})
        packed = (
            document.tobytes(garbage=4, deflate=True, use_objstms=1)
            if figures else source.read_bytes()
        )

    with pikepdf.open(io.BytesIO(packed)) as pdf:
        pdf.remove_unreferenced_resources()
        pdf.save(
            destination,
            linearize=True,
            compress_streams=True,
            recompress_flate=True,
            object_stream_mode=pikepdf.ObjectStreamMode.preserve,
        )
    with pikepdf.open(destination) as verified:
        if not verified.check_linearization() or verified.check_pdf_syntax():
            raise ValueError("PDF did not pass syntax and progressive-loading checks")
    print(json.dumps({
        "source": str(source), "destination": str(destination),
        "before": source.stat().st_size, "after": destination.stat().st_size,
        "restored": restored,
    }))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--figures", type=Path)
    arguments = parser.parse_args()
    if arguments.source.resolve() == arguments.destination.resolve():
        parser.error("Use a separate output path, then verify it before replacing the original.")
    optimize(arguments.source, arguments.destination, arguments.figures)

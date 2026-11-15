"""Rebuild index.html from the template and the itinerary data.

Usage: python3 src/build.py
"""
from pathlib import Path

root = Path(__file__).resolve().parent
template = (root / "app.template.html").read_text(encoding="utf-8")
data = (root / "data.json").read_text(encoding="utf-8")
(root.parent / "index.html").write_text(template.replace("__DATA__", data), encoding="utf-8")
print("index.html rebuilt")

"""Build the two versions of the app.

  index.html                 Web version (GitHub Pages / any host). Contains NO itinerary data:
                             it loads the trip from Supabase after you sign in.
  dist/claude-artifact.html  Claude artifact version. Itinerary embedded; saves to the artifact's own storage.

Usage: python3 src/build.py
"""
import json
from pathlib import Path

root = Path(__file__).resolve().parent
template = (root / "app.template.html").read_text(encoding="utf-8")
data = (root / "data.json").read_text(encoding="utf-8")
supabase = json.dumps({
    "url": "https://mepfsxfbpfnnudvlijgs.supabase.co",
    # Publishable (public) key: safe in the browser; access is enforced by row-level security.
    "key": "sb_publishable_NjbB_3tU424OkS7jL1_Utw_4m00lOAH",
})

facts = {}
for f in sorted((root / "facts").glob("*.txt")):
    facts[f.stem] = [l.strip() for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
template = template.replace("__FACTS__", json.dumps(facts, ensure_ascii=False))

web = template.replace("__DATA__", "null").replace("__SBCONF__", supabase)
artifact = template.replace("__DATA__", data).replace("__SBCONF__", "null")

(root.parent / "index.html").write_text(web, encoding="utf-8")
(root.parent / "dist").mkdir(exist_ok=True)
(root.parent / "dist" / "claude-artifact.html").write_text(artifact, encoding="utf-8")
print("built index.html (web) and dist/claude-artifact.html (Claude)")

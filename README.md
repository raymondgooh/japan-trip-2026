# Japan Trip Companion · 21 Nov – 4 Dec 2026

A single-page web app for the Japan trip: Tokyo (Akabane) → Kawaguchiko → Kyoto → Sapporo.

Built from `Japan_Itinerary_Final_Working_Plan_21Nov-4Dec2026.xlsm`.

## What's in it

- **Today**: countdown before the trip; "up next" in Japan time during it
- **Itinerary**: day-by-day timeline with edit, add-stop (＋), shift-times slider, done ticks, trip photos/videos and note pictures
- **Budget**: estimated vs paid by day and by category, plus pre-trip costs
- **Bookings, Stays & flights, Tips**
- **Settings**: display currency (IDR / JPY / MYR / SGD), exchange rates, people, snow-day option, cost categories

## Files

| File | Purpose |
|---|---|
| `index.html` | The built app (open it in a browser) |
| `src/app.template.html` | App source with a `__DATA__` placeholder |
| `src/data.json` | Itinerary data extracted from the spreadsheet |
| `src/build.py` | Rebuilds `index.html` from the two files above |

## Where the data is saved

The live version runs as a Claude artifact, where edits, costs, photos and videos are saved to the artifact's
own database and file storage and shared with everyone who can edit it.

Opened anywhere else (a local file, GitHub Pages), the app falls back to **this device only**: edits are kept in
the browser's local storage and photo/video uploads are turned off.

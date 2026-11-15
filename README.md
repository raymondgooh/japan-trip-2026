# Japan Trip Companion · 21 Nov – 4 Dec 2026

A single-page web app for the Japan trip: Tokyo (Akabane) → Kawaguchiko → Kyoto → Sapporo.
Built from `Japan_Itinerary_Final_Working_Plan_21Nov-4Dec2026.xlsm`.

## What's in it

- **Today**: countdown before the trip; "up next" in Japan time during it
- **Itinerary**: day-by-day timeline with edit, add-stop (＋), shift-times slider, done ticks, trip photos/videos and note pictures
- **Budget**: estimated vs paid by day and by category, plus pre-trip costs
- **Bookings, Stays & flights, Tips**
- **Settings**: display currency (IDR / JPY / MYR / SGD), exchange rates, people, snow-day option, cost categories, account

## Two versions

| File | Where it runs | Itinerary | Saves to |
|---|---|---|---|
| `index.html` | Any web host (e.g. GitHub Pages) or opened directly | Loaded from Supabase after sign-in; **not** in the file | Supabase (`japan-trip-2026` project) |
| `dist/claude-artifact.html` | The Claude artifact | Embedded | The artifact's own storage |

The two keep separate data.

### Web version (`index.html`) and Supabase

- Sign in with email + password. Only emails in `trip_members` can read or change anything; everyone else sees nothing.
- `trip_docs` holds `base/itinerary`, `days/<date>`, `settings/main` and `pretrip/main` as JSON. Changes sync live between devices.
- Photos, videos and note pictures go to the private `trip-media` storage bucket (20 MB per file).
- After the first sign-in the itinerary is cached on the device, so it still opens without signal. Edits made offline are **not** queued for later: the badge shows "Save failed", so make important edits with a connection.
- The publishable key in `src/build.py` is meant to be public; security comes from row-level security (`supabase/schema.sql`).

## Files

| File | Purpose |
|---|---|
| `src/app.template.html` | App source (`__DATA__` and `__SBCONF__` placeholders) |
| `src/data.json` | Itinerary data extracted from the spreadsheet (personal: keep the repo private, or remove this file before making it public) |
| `src/build.py` | Builds `index.html` and `dist/claude-artifact.html` |
| `supabase/schema.sql` | Database tables, access rules and storage bucket |

Rebuild after editing: `python3 src/build.py`

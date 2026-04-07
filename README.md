 # Private Tools

 This repository hosts two cooperating utilities: a Vue 3/Vite frontend that presents helpers for formatting and PDF splitting, and a Python FastAPI backend that handles roster matching and ZIP generation for the team-split workflow.

 ## Tools

 ### Date Formatter

 - Paste or type messy date strings into the composer and get instant conversions across multiple formats (ISO, locale-aware, Excel friendly).
 - Auto-detect common delimiters, add leading zeros, and normalize time zones so you can copy clean dates into other apps without context switching.
 - Drop the formatted result back into Excel, a spreadsheet tab, or any clipboard target using the built-in copy buttons.

 ### Text Formatter

 - Highlight and normalize whitespace, add or remove bullets, and break single-line dumps into tidy lists or tables.
 - Paste notes from a feed or chat, then use the live preview to trim padding, replace repeated separators, and ensure consistent casing before copying.
 - Includes shortcuts for emoji-safe pasting, forced wrapping, and flagging suspicious characters before you share.

 ### PDF Team Splitter

 - The Vue frontend uploads a roster workbook and a PDF to `/api/pdf-team-split`, lets you tweak the sheet/column options, and downloads a ZIP with one file per team.
 - The FastAPI backend in `server/` peels apart uploads, applies fuzzy matching, and streams the resulting archive back for download.
 - Frontend and backend both live in this repo so you can iterate locally before deploying to 1Panel, a reverse-proxied archive, or any in-house host.

 ## Local development

 ### Frontend (Vue 3 + Vite)

 1. `npm install` (or `npm ci` after cloning)
 2. `npm run dev` to start the Vite dev server (port 5173 by default)
 3. `npm run build` to emit production assets into `dist`
 4. `npm run preview -- --host 0.0.0.0 --port 4173` if you want to smoke-test the built bundle locally

 ### Backend (FastAPI)

 1. `py -3.12 -m pip install -r server/requirements.txt`
 2. `py -3.12 -m uvicorn server.app:app --reload --host 0.0.0.0 --port 8000`
 3. Point the frontend at `http://localhost:8000/api` when you need to call the team-split service.
 4. Run `py -3.12 -m pytest server/tests -v` after installing dependencies to keep the validation suite green.

 ## Verification

 Run the following commands before shipping changes:

 - `py -3.12 -m pytest server/tests -v`
 - `npm run test`
 - `npm run type-check`
 - `npm run build`

# SIH UI 2 Project - Local Development

## Backend (Flask)
Env vars (optional, defaults shown):
- `FRONTEND_ORIGINS`: http://localhost:5173,http://127.0.0.1:5173
- `BACKEND_HOST`: 0.0.0.0
- `BACKEND_PORT`: 5000
- `API_MODE`: true (skips audio init; uses fallback AI if GROQ_API_KEY missing)
- `GROQ_API_KEY`: set for live AI answers

Run:
```powershell
cd "c:\Users\Madhu\OneDrive\Documents\SIH UI 2\project"
$env:FRONTEND_ORIGINS = 'http://localhost:5173,http://127.0.0.1:5173'
$env:BACKEND_HOST = '0.0.0.0'
$env:BACKEND_PORT = '5000'
$env:API_MODE = 'true'
python .\Backend1.py
```
Health check: http://localhost:5000/health

## Frontend (Vite React)
- `src/utils/api.ts` reads `VITE_API_BASE` (see `.env.development`)
- Default: `http://localhost:5000`

Run:
```powershell
npm install
npm run dev
```
Open the URL shown by Vite (usually http://localhost:5173)

## Notes
- The chat interface now calls the backend `/followup` endpoint for AI answers.
- If you get CORS errors, confirm FRONTEND_ORIGINS matches your dev server URL.

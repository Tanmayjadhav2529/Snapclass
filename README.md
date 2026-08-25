# SnapClass - AI-Powered Attendance System

Face and voice recognition based attendance for classrooms, powered by Streamlit and Supabase.

SnapClass helps teachers record classroom attendance quickly by identifying enrolled students through classroom photos or recorded audio, while giving students an easy way to join subjects and view their attendance records.

## Live Demo

[Open SnapClass](https://snapclass-landing-page-liard.vercel.app/)

## Features

- Teacher and student login and registration with secure password hashing using `bcrypt`
- Face-recognition-based attendance from uploaded or captured classroom photos
- AI face detection and matching against enrolled student profiles
- Voice-recognition-based attendance from recorded classroom audio using SpeechBrain
- Subject creation and management with shareable join codes for student self-enrollment
- Attendance history and records grouped by session and subject
- Cloud-based backend using Supabase (Postgres)

## Tech Stack

| Area | Technology |
| --- | --- |
| Frontend | Streamlit |
| Backend / Database | Supabase (Postgres) |
| Face Recognition | `face_recognition` models / dlib |
| Voice Recognition | SpeechBrain, librosa, PyTorch, torchaudio |
| Authentication | `bcrypt` password hashing |
| Deployment | Streamlit Community Cloud |

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/Tanmayjadhav2529/Snapclass.git
cd Snapclass
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Supabase secrets

The application reads the following values through Streamlit secrets:

- `SUPABASE_URL`
- `SUPABASE_SECRET_KEY`

For local development, place them in `.streamlit/secrets.toml`:

```toml
SUPABASE_URL = "your-supabase-project-url"
SUPABASE_SECRET_KEY = "your-supabase-api-key"
```

You may also provide equivalent environment configuration through your deployment setup. Do not commit credentials to Git.

### 5. Run the application

```bash
streamlit run app.py
```

## Project Structure

```text
.
├── app.py                         # Streamlit application entry point
├── requirements.txt               # Python dependencies
├── src/
│   ├── database/                  # Supabase client and database operations
│   ├── screens/                   # Home, teacher, and student screens
│   ├── components/                # Dialogs, headers, footers, and subject cards
│   ├── pipelines/                 # Face and voice recognition pipelines
│   └── ui/                        # Shared layout and styling helpers
└── README.md
```

## License

MIT

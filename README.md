# RoWordNet Similarity

A web application for computing semantic similarity between Romanian words using RoWordNet (Romanian WordNet). The application implements 8 different similarity algorithms from scratch.

## Features

- **8 Similarity Algorithms**: PATH, WUP, LCH, RES, JCN, LIN, LESK, HSO
- **Modern UI**: Dark theme with gradient accents and glassmorphism
- **Synset Information**: View synset details including definitions
- **Visual Comparison**: Similarity bars for easy comparison

## Project Structure

```
NLP-Project/
├── backend/                    # FastAPI Python backend
│   ├── main.py                 # API endpoints
│   ├── rowordnet_loader.py     # RoWordNet pickle loader
│   ├── requirements.txt        # Python dependencies
│   └── algorithms/             # Similarity algorithms
│       ├── path_similarity.py  # PATH: 1/path_length
│       ├── wup_similarity.py   # WUP: Wu-Palmer
│       ├── lch_similarity.py   # LCH: Leacock-Chodorow
│       ├── res_similarity.py   # RES: Resnik IC
│       ├── jcn_similarity.py   # JCN: Jiang-Conrath
│       ├── lin_similarity.py   # LIN: Lin normalized IC
│       ├── lesk_similarity.py  # LESK: Gloss overlap
│       └── hso_similarity.py   # HSO: Hirst-St-Onge
├── frontend/                   # Next.js React frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx        # Main page
│   │   │   ├── layout.tsx      # Root layout
│   │   │   └── globals.css     # Global styles
│   │   └── components/
│   │       ├── SimilarityForm.tsx
│   │       └── ResultsTable.tsx
│   ├── package.json
│   └── next.config.js
└── rowordnet.pickle            # RoWordNet data file
```

## Algorithms

| Algorithm | Formula | Description |
|-----------|---------|-------------|
| **PATH** | `1 / path_length` | Inverse of shortest path between synsets |
| **WUP** | `2*depth(LCS) / (depth(s1)+depth(s2))` | Wu-Palmer depth-based similarity |
| **LCH** | `-log(path / 2*max_depth)` | Leacock-Chodorow log-scaled path |
| **RES** | `IC(LCS)` | Resnik Information Content of LCS |
| **JCN** | `1 / (IC(s1)+IC(s2)-2*IC(LCS))` | Jiang-Conrath IC distance |
| **LIN** | `2*IC(LCS) / (IC(s1)+IC(s2))` | Lin normalized IC similarity |
| **LESK** | `gloss_overlap` | Word overlap in definitions |
| **HSO** | `C - path - k*dir_changes` | Hirst-St-Onge with direction penalty |

## Requirements

### Backend
- Python 3.8+
- FastAPI
- Uvicorn
- NetworkX

### Frontend
- Node.js 18+
- npm or yarn

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd NLP-Project
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

## Running the Application

### 1. Start the Backend Server

```bash
cd backend
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### 2. Start the Frontend Server

In a new terminal:

```bash
cd frontend
npm run dev
```

The web application will be available at `http://localhost:3000`

## Usage

1. Open the web browser and navigate to `http://localhost:3000`
2. Enter two Romanian words in the input fields
3. Click "Calculate Similarity" or use one of the example word pairs
4. View the similarity scores from all 8 algorithms
5. See synset details for both words

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/similarity` | POST | Calculate similarity between two words |
| `/synsets/{word}` | GET | Get synsets for a word |
| `/algorithms` | GET | List available algorithms |

### Example API Request

```bash
curl -X POST http://localhost:8000/similarity \
  -H "Content-Type: application/json" \
  -d '{"word1": "caine", "word2": "pisica"}'
```

## Troubleshooting

### PowerShell Script Execution Error (Windows)

If you see an error about scripts being disabled:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Or run commands using `cmd` instead of PowerShell.

### RoWordNet Loading Issues

Make sure `rowordnet.pickle` is in the project root directory (same level as `backend/` and `frontend/` folders).

## License

This project is for educational purposes - NLP Course Project.

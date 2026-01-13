# RoWordNet Similarity

A web application for computing semantic similarity between Romanian words using 8 different algorithms, similar to [WS4J](http://ws4jdemo.appspot.com/) for English.

![RoWordNet Similarity](https://img.shields.io/badge/Language-Romanian-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![Next.js](https://img.shields.io/badge/Next.js-14-black)

## Features

- **8 Similarity Algorithms**: PATH, WUP, LCH, RES, JCN, LIN, LESK, HSO
- **Word Similarity**: Compare individual words with sense selection (word#pos#sense)
- **Sentence Similarity**: Compare sentences with similarity matrix visualization
- **Romanian Lemmatization**: Handles inflected word forms
- **Modern UI**: Dark theme with glassmorphism effects

## Quick Start (Windows)

### Prerequisites

1. **Python 3.8+** - Install from [python.org](https://www.python.org/downloads/) or use [Anaconda](https://www.anaconda.com/download)
2. **Node.js 18+** - Install from [nodejs.org](https://nodejs.org/)

### Running the Application

1. **Double-click `START_APP.bat`**
2. Wait for the servers to start
3. Browser will open automatically at http://localhost:3000
4. **Close the command window to stop the application**

## Manual Installation

### Backend (Python/FastAPI)

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

Then open http://localhost:3000 in your browser.

## Usage

### Word Similarity

Enter two Romanian words to compare. Use the format `word#pos#sense` for specific senses:
- `câine` - any sense
- `câine#n#1` - noun, first sense
- `merge#v#1` - verb, first sense

**POS codes**: n (noun), v (verb), a (adjective), r (adverb)

### Sentence Similarity

Enter two sentences in Romanian. The app will:
1. Tokenize and lemmatize words
2. Find words in RoWordNet
3. Build a similarity matrix
4. Calculate overall sentence similarity

Words not found in RoWordNet are marked with ~~strikethrough~~.

## Algorithms

| Algorithm | Formula | Description |
|-----------|---------|-------------|
| PATH | 1 / path_length | Inverse of shortest path |
| WUP | 2*depth(LCS) / (depth(s1)+depth(s2)) | Wu-Palmer similarity |
| LCH | -log(path / 2*max_depth) | Leacock-Chodorow |
| RES | IC(LCS) | Resnik (Information Content) |
| JCN | 1 / (IC(s1)+IC(s2)-2*IC(LCS)) | Jiang-Conrath |
| LIN | 2*IC(LCS) / (IC(s1)+IC(s2)) | Lin similarity |
| LESK | gloss_overlap | Gloss overlap count |
| HSO | C - path - k*dir_changes | Hirst-St-Onge |

## Project Structure

```
NLP-Project/
├── START_APP.bat          # Windows launcher
├── STOP_APP.bat           # Stop servers
├── rowordnet.pickle       # RoWordNet database (required)
├── backend/
│   ├── main.py            # FastAPI application
│   ├── rowordnet_loader.py
│   ├── lemmatizer.py      # Romanian lemmatizer
│   ├── requirements.txt
│   └── algorithms/        # Similarity implementations
└── frontend/
    ├── package.json
    └── src/
        ├── app/
        └── components/
```

## Limitations

- RoWordNet has limited vocabulary (~50k synsets vs ~117k in English WordNet)
- Not all word senses are included
- Works best with nouns in base form (lemmas)
- Requires Romanian diacritics (ă, â, î, ș, ț)

## API Endpoints

- `POST /similarity` - Calculate word similarity
- `POST /sentence-similarity` - Calculate sentence similarity
- `GET /synsets/{word}` - Get synsets for a word
- `GET /algorithms` - List available algorithms
- `GET /health` - Health check

## Technologies

- **Backend**: Python, FastAPI, RoWordNet
- **Frontend**: Next.js, React, TypeScript
- **Styling**: CSS with glassmorphism effects

## Authors

NLP Project - Faculty Project

## License

MIT License

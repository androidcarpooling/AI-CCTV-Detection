# Quick Start Guide

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) Create a `.env` file from `.env.example`:
```bash
cp .env.example .env
```

## Usage Examples

### 1. Build Watchlist from Photos

Place your photos in a directory (one person per photo, or multiple photos per person):

```bash
python main.py build-watchlist --photos-dir ./photos --output-db watchlist.db
```

This will:
- Detect faces in each photo
- Generate embeddings using ArcFace
- Store them in the database

### 2. Process a Video File

```bash
python main.py process-video --video ./demo.mp4 --watchlist watchlist.db --output results.json
```

Options:
- `--fps 5`: Process every 5th frame (default: 1 = all frames)
- `--threshold 0.4`: Adjust similarity threshold (default: 0.35)

### 3. Process RTSP CCTV Stream

```bash
python main.py process-rtsp --rtsp-url rtsp://username:password@camera-ip:554/stream --watchlist watchlist.db
```

This runs continuously until interrupted (Ctrl+C).

### 4. Process a Single Image

```bash
python main.py process-image --image ./test.jpg --watchlist watchlist.db
```

### 5. Start Web Dashboard

```bash
python main.py dashboard --port 5000 --watchlist watchlist.db
```

Then open http://localhost:5000 in your browser.

## Python API Usage

You can also use the system programmatically:

```python
from database import Database
from processor import FaceRecognitionProcessor

# Initialize database
db = Database()

# Initialize processor
processor = FaceRecognitionProcessor(db, similarity_threshold=0.35)

# Build watchlist
processor.build_watchlist('./photos', person_id_prefix='person')

# Process video
results = processor.process_video('./video.mp4', output_file='results.json')

# Process image
results = processor.process_image('./test.jpg')

# Process RTSP stream (runs until interrupted)
processor.process_rtsp('rtsp://camera-url')
```

## Database Options

### SQLite (Default)
```python
db = Database()  # Uses watchlist.db by default
```

### PostgreSQL
```python
db = Database(
    db_type='postgresql',
    connection_string='postgresql://user:pass@localhost:5432/dbname'
)
```

### Redis
```python
db = Database(db_type='redis')
```

## Configuration

Edit `config.py` or set environment variables:

- `SIMILARITY_THRESHOLD`: Matching threshold (default: 0.35)
- `RECOGNIZER_MODEL`: 'buffalo_l' or 'glint360k_r100_fp16'
- `DATABASE_TYPE`: 'sqlite', 'postgresql', or 'redis'

## Notes

- First run will download InsightFace models automatically
- Models are cached in `~/.insightface/`
- For GPU acceleration, change `CPUExecutionProvider` to `CUDAExecutionProvider` in `face_detector.py` and `face_recognizer.py`
- Similarity threshold of 0.35 is tuned for CCTV scenarios (lower = stricter matching)


# Hybrid Property Recommender with MLOps

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-blue.svg" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg" alt="FastAPI 0.115+">
  <img src="https://img.shields.io/badge/scikit--learn-1.5%2B-F7931E.svg" alt="Scikit-learn 1.5+">
  <img src="https://img.shields.io/badge/FAISS-1.9%2B-0467DF.svg" alt="FAISS 1.9+">
  <img src="https://img.shields.io/badge/LightGBM-4.5%2B-02569B.svg" alt="LightGBM 4.5+">
  <img src="https://img.shields.io/badge/MLflow-3.0%2B-0194E2.svg" alt="MLflow 3.0+">
  <img src="https://img.shields.io/badge/Next.js-16.2-000000.svg" alt="Next.js 16.2">
  <img src="https://img.shields.io/badge/Mapbox%20GL-3.26-4264FB.svg" alt="Mapbox GL 3.26">
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED.svg" alt="Docker Compose">
</p>

## Business Problem

Short-stay platforms can have thousands of properties. Users must compare price, location, room type, amenities, rating, and availability. Normal filters help, but they do not learn what a user may prefer.

Popular listings can also appear too often, while new users and new properties have little history. This makes it harder to return useful and varied results.

## How It Solves the Problem

This system uses a two-stage recommendation flow. The first stage finds a small group of suitable properties. It uses hard filters, property text, FAISS vector search, and review-history signals. The second stage ranks those candidates by query match, budget fit, amenities, location, rating, popularity, and availability.

The system also supports users and properties with no history. It uses the available preferences and listing details to build cold-start results. Each result includes a match score and short reasons, so the ranking is easier to understand.

FastAPI serves the recommendations. The Next.js interface provides search filters, saved properties, comparison, and a Mapbox map. MLflow records training runs and model settings.

The project uses public review history as positive feedback. A review does not show impressions, dislikes, saves, or booking conversion, so it is not a full view of user behaviour.

## How a Recommendation Moves Through the System

The system creates recommendations in these steps:

1. The API reads the search query and user preferences.
2. Hard filters remove properties outside the budget or request.
3. TF-IDF and FAISS find properties with similar text and amenities.
4. Review history adds an item-to-item collaborative score when user history exists.
5. The hybrid retriever combines the candidate sources.
6. The baseline or LightGBM ranker scores each candidate.
7. Diversity reranking reduces repeated areas and property types.
8. The API returns the top properties with match reasons.

The weighted ranker works without model training and is the default. The LightGBM ranker is optional and should only be used after it performs better in offline evaluation.

## Main Features

### Hybrid candidate retrieval

- Hard filters check budget, bedrooms, property type, and location.
- TF-IDF creates vectors from title, description, area, room type, and amenities.
- FAISS searches the property vectors quickly.
- Item-to-item collaborative scores use users who reviewed more than one property.
- The hybrid retriever combines content and collaborative signals.

### Ranking and personalization

- The weighted baseline scores query match, budget fit, amenities, location, rating, popularity, and availability.
- LightGBM LambdaRank can learn ranking weights from interaction data.
- User history creates simple preferences for areas, property types, price, and amenities.
- Diversity reranking reduces repeated results.

### Cold-start recommendations

- New users receive results from their search and selected preferences.
- Users without preferences receive useful properties based on rating, popularity, and availability.
- New properties can appear through their text and metadata before they have reviews.

### Recommendation explanations

Each result can show reasons such as:

- Within budget
- Matches selected amenities
- Near the preferred area
- Strong guest rating
- Similar to the search text

### Offline evaluation and MLflow

- The latest interaction for each user is held out for testing.
- The project reports Precision@K, Recall@K, MAP@K, NDCG@K, and catalogue coverage.
- The baseline and LightGBM ranker are evaluated with the same split.
- MLflow stores model parameters and training artifacts.
- The learned model is saved at `artifacts/models/lgbm_ranker.joblib`.

### API and frontend

- `POST /api/v1/recommendations` returns ranked properties.
- `GET /health` supports service and Docker health checks.
- Pydantic validates API requests and responses.
- The Next.js interface supports filters, saved items, comparison, and result reasons.
- Mapbox GL shows property markers and listing details.

### Code Structure

- `src/app/data` loads, cleans, validates, and splits the data.
- `src/app/features` builds property, user, interaction, and text features.
- `src/app/retrieval` finds candidates with content and collaborative search.
- `src/app/ranking` holds the weighted, LightGBM, and diversity rankers.
- `src/app/recommendation` creates final results and explanations.
- `src/app/evaluation` holds ranking metrics and error analysis.
- `src/app/pipelines` downloads data, prepares files, trains models, and runs evaluation.
- `src/app/apis` holds the FastAPI routes.
- `frontend` holds the Next.js and Mapbox interface.

## Project Structure

```text
hybrid-property-recommender-mlops/
├── artifacts/
│   ├── indexes/
│   ├── models/
│   └── evaluation.json
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_features_and_baselines.ipynb
│   ├── 03_hybrid_retrieval_and_ranking.ipynb
│   └── 04_evaluation_and_error_analysis.ipynb
├── src/
│   └── app/
│       ├── apis/
│       ├── data/
│       ├── evaluation/
│       ├── features/
│       ├── monitoring/
│       ├── pipelines/
│       ├── ranking/
│       ├── recommendation/
│       ├── retrieval/
│       ├── config.py
│       ├── dependencies.py
│       ├── main.py
│       └── schemas.py
├── frontend/
│   ├── app/
│   ├── components/
│   ├── public/
│   └── package.json
├── tests/
│   ├── fixtures/
│   ├── integration/
│   └── unit/
├── .env.example
├── .gitignore
├── Dockerfile
├── LICENSE
├── Makefile
├── README.md
├── docker-compose.yml
├── pyproject.toml
└── uv.lock
```

## Data Source

The project uses the Berlin data from [Inside Airbnb](https://insideairbnb.com/get-the-data/). The download command uses the snapshot dated 26 June 2026.

- `listings.csv.gz` contains property text, room type, price, amenities, rating, availability, and coordinates.
- `reviews.csv.gz` provides positive user-property interactions.
- `neighbourhoods.geojson` contains Berlin area boundaries.

Inside Airbnb provides the data under the CC BY 4.0 license. During preparation, reviewer IDs are salted and hashed. Reviewer names and review text are not stored.

Downloaded and processed data are not included in the repository. A small sample dataset is included for local checks.

## Steps to Run the Project

The project needs Python 3.11 or later, Node.js 22.13 or later, `uv`, and a public Mapbox token.

### 1. Open the project folder

```bash
cd hybrid-property-recommender-mlops
```

### 2. Install the Python packages

```bash
uv sync --extra ml --extra dev --extra notebooks
```

`uv` creates `.venv` and installs the locked package versions.

### 3. Create the environment files

```bash
cp .env.example .env
cp frontend/.env.example frontend/.env.local
```

Open `frontend/.env.local` and add a public Mapbox token:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MAPBOX_TOKEN=your-public-mapbox-token
```

The frontend reads the token from `NEXT_PUBLIC_MAPBOX_TOKEN`. The map does not use a second map provider.

### 4. Install the frontend packages

```bash
npm --prefix frontend ci
```

### 5. Download and prepare the real data

```bash
uv run python -m app.pipelines.download_data
uv run python -m app.pipelines.prepare_data
```

The prepared files are saved in `data/processed`.

### 6. Train the optional LightGBM ranker

```bash
uv run python -m app.pipelines.train_ranker --skip-prepare --max-users 1500
```

Training saves the model in `artifacts/models` and records the run in MLflow.

### 7. Run offline evaluation

```bash
uv run python -m app.pipelines.evaluate_model --k 10 --max-users 500
```

The metrics are saved in `artifacts/evaluation.json`.

### 8. Run the checks

```bash
uv run pytest
uv run ruff check src tests
npm --prefix frontend run lint
npm --prefix frontend run build
```

### 9. Start the API

```bash
uv run uvicorn app.main:app --app-dir src --reload
```

### 10. Start the frontend

Open a second terminal:

```bash
npm --prefix frontend run dev
```

### 11. Open the application

- Frontend: `http://localhost:3000`
- API documentation: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

## Send a Test API Request

Keep the API running. Open another terminal and run:

```bash
curl -X POST http://localhost:8000/api/v1/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "query": "entire apartment in Berlin with Wifi and kitchen",
    "city": "Berlin",
    "max_budget": 180,
    "bedrooms": 2,
    "property_types": ["Entire home/apt"],
    "amenities": ["Wifi", "Kitchen", "Washer"],
    "top_k": 5
  }'
```

## Run with Docker Compose

Add the Mapbox token before starting the containers:

```bash
export NEXT_PUBLIC_MAPBOX_TOKEN="your-public-mapbox-token"
docker compose up --build
```

Docker Compose starts these services:

- FastAPI on `http://localhost:8000`
- Next.js on `http://localhost:3000`
- MLflow on `http://localhost:5000`

Stop the services with:

```bash
docker compose down
```

## Open the Notebooks

```bash
uv run jupyter lab
```

Run the notebooks in number order:

1. `01_data_exploration.ipynb` checks data quality, prices, areas, and interaction sparsity.
2. `02_features_and_baselines.ipynb` creates features and compares simple baselines.
3. `03_hybrid_retrieval_and_ranking.ipynb` tests retrieval, ranking, and explanations.
4. `04_evaluation_and_error_analysis.ipynb` compares metrics, coverage, user groups, and errors.

The notebooks use processed Inside Airbnb data when it is available. Otherwise, they use the small sample data.

The weighted baseline has better ranking metrics. LightGBM has higher catalogue coverage, but it is not used by the API. Set `USE_LEARNED_RANKER=true` only after a learned model performs better than the baseline.


set -e

echo ""
echo "AttritionIQ — Starting up..."
echo "─────────────────────────────────"

if ! command -v docker &> /dev/null; then
  echo "Docker not found. Please install Docker Desktop."
  exit 1
fi

if ! command -v docker-compose &> /dev/null; then
  echo " docker-compose not found. Please install it."
  exit 1
fi

if [ ! -f "./data/HRDataset_v14.csv" ]; then
  echo " Dataset not found at ./data/HRDataset_v14.csv"
  echo "   Please place the HR dataset file in the ./data/ folder."
  exit 1
fi

if [ ! -f ".env" ]; then
  echo "Creating .env from template..."
  cp .env.example .env
  echo ".env created. API_KEY set to dev default."
fi

echo ""
echo "Building Docker containers..."
docker-compose build

echo ""
echo "Starting services..."
docker-compose up -d

echo ""
echo "Waiting for backend to be ready (model training ~30s)..."
sleep 5

for i in {1..20}; do
  if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "Backend is ready."
    break
  fi
  echo "   Waiting... ($i/20)"
  sleep 3
done

echo ""
echo "─────────────────────────────────"
echo "AttritionIQ is running!"
echo ""
echo "   Frontend: http://localhost:3000"
echo "   API Docs: http://localhost:8000/docs"
echo "   API Key: (see .env file)"
echo ""
echo "   To stop: docker-compose down"
echo "─────────────────────────────────"

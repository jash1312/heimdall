# Product Price Comparison Tool

A generic tool that fetches product prices from multiple websites based on the country the consumer is shopping from. The tool supports multiple countries and product categories, with AI-based product matching for accurate results.

## Features

- **Multi-country support**: US, India, and extensible to other countries
- **Multiple retailers**: Amazon, Flipkart, Walmart, and more
- **AI-powered matching**: Intelligent product matching using LLM-based algorithms
- **Robust scraping**: Anti-detection measures with requests
- **Best price selection**: Shows the best (lowest price) result from each site
- **REST API**: Serverless API endpoint for easy integration

## Supported Countries and Retailers

| Country | Retailers |
|---------|-----------|
| US | Amazon US, Walmart |
| India | Amazon India, Flipkart |

## Quick Start

### Prerequisites

- Python 3.8+
- Git

### Installation (for local testing)

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd heimdall
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the API locally**
   ```bash
   uvicorn api.fetch_prices:app --reload
   ```
   (Or use Flask if you prefer)

## Vercel Deployment

1. Push this repo to GitHub.
2. Import the repo in Vercel (https://vercel.com/new).
3. Vercel will auto-detect the `api/` directory and deploy `api/fetch_prices.py` as a serverless function.
4. The API will be available at:
   ```
   https://<your-vercel-domain>/api/fetch_prices
   ```

## API Usage

### Endpoint
`POST /api/fetch_prices`

### Request Format
```json
{
  "country": "US",
  "query": "iPhone 16 Pro, 128GB"
}
```

### Response Format
```json
[
  {
    "link": "https://www.amazon.com/...",
    "price": "999",
    "currency": "USD",
    "productName": "Apple iPhone 16 Pro 128GB",
    "source": "Amazon"
  },
  ...
]
```

## Testing with cURL

### Test the required query: iPhone 16 Pro, 128GB in US
```bash
curl -X POST https://<your-vercel-domain>/api/fetch_prices \
  -H "Content-Type: application/json" \
  -d '{"country": "US", "query": "iPhone 16 Pro, 128GB"}'
```

### Test Indian product: boAt Airdopes 311 Pro
```bash
curl -X POST https://<your-vercel-domain>/api/fetch_prices \
  -H "Content-Type: application/json" \
  -d '{"country": "IN", "query": "boAt Airdopes 311 Pro"}'
```

## Project Structure

```
├── api/
│   └── fetch_prices.py      # Serverless API logic
├── public/                  # (Optional) Frontend static files
├── requirements.txt         # Python dependencies
├── vercel.json              # Vercel configuration
├── README.md                # This file
└── task.txt                 # Original task requirements
```

## Key Components

### 1. Connectors
- **Amazon US**: Web scraping with anti-detection measures
- **Amazon India**: Requests-based scraping for robust results
- **Flipkart**: Mock implementation (easily extensible)
- **Walmart**: Mock implementation (easily extensible)

### 2. Product Matching
- AI-based matching using word intersection
- Normalized query processing
- Configurable matching thresholds

### 3. Price Extraction
- Multiple price selector strategies
- Currency detection and normalization
- Robust error handling

### 4. Anti-Detection Measures
- Random user agents
- Request delays
- Retry mechanisms

## Configuration

### Adding New Countries
Edit the `SITE_MAP` in `api/fetch_prices.py`:
```python
SITE_MAP = {
    "US": ["Amazon", "Walmart"],
    "IN": ["AmazonIN", "Flipkart"],
    "UK": ["AmazonUK", "Argos"],  # Add new country
}
```

### Adding New Retailers
1. Create a connector function
2. Add it to the `CONNECTORS` registry
3. Update the `SITE_MAP` for relevant countries

## Troubleshooting

If you encounter issues, please open an issue on GitHub or contact the maintainer. 
# Product Price Comparison Tool

A generic tool that fetches product prices from multiple websites based on the country the consumer is shopping from. The tool supports multiple countries and product categories, with AI-based product matching for accurate results.

## Features

- **Multi-country support**: US, India, and extensible to other countries
- **Multiple retailers**: Amazon, Flipkart, Walmart, and more
- **AI-powered matching**: Intelligent product matching using LLM-based algorithms
- **Robust scraping**: Anti-detection measures with Selenium and requests
- **Best price selection**: Shows the best (lowest price) result from each site
- **Multiple interfaces**: REST API, CLI, and Streamlit web UI

## Supported Countries and Retailers

| Country | Retailers |
|---------|-----------|
| US | Amazon US, Walmart |
| India | Amazon India, Flipkart |

## Quick Start

### Prerequisites

- Python 3.8+
- Chrome browser (for Selenium scraping)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd online
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

4. **Install Chrome WebDriver** (automatically handled by webdriver-manager)

### Running the Application

#### Option 1: Streamlit Web UI (Recommended)
```bash
streamlit run streamlit_app.py
```
Access the web interface at: http://localhost:8501

#### Option 2: Flask API Server
```bash
python main.py serve
```
API will be available at: http://localhost:5000

#### Option 3: Command Line Interface
```bash
python main.py
```

## API Usage

### Endpoint
`POST /fetch_prices`

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
  {
    "link": "https://www.walmart.com/...",
    "price": "999",
    "currency": "USD",
    "productName": "Apple iPhone 16 Pro 128GB",
    "source": "Walmart"
  }
]
```

## Testing with cURL

### Test the required query: iPhone 16 Pro, 128GB in US
```bash
curl -X POST http://localhost:5000/fetch_prices \
  -H "Content-Type: application/json" \
  -d '{"country": "US", "query": "iPhone 16 Pro, 128GB"}'
```

### Test Indian product: boAt Airdopes 311 Pro
```bash
curl -X POST http://localhost:5000/fetch_prices \
  -H "Content-Type: application/json" \
  -d '{"country": "IN", "query": "boAt Airdopes 311 Pro"}'
```

### Test with different products
```bash
# Laptop search in US
curl -X POST http://localhost:5000/fetch_prices \
  -H "Content-Type: application/json" \
  -d '{"country": "US", "query": "MacBook Pro 14 inch"}'

# Mobile search in India
curl -X POST http://localhost:5000/fetch_prices \
  -H "Content-Type: application/json" \
  -d '{"country": "IN", "query": "Samsung Galaxy S24"}'
```

## Docker Setup (Alternative)

### Build and run with Docker
```bash
# Build the image
docker build -t price-comparison-tool .

# Run the container
docker run -p 5000:5000 -p 8501:8501 price-comparison-tool
```

## Project Structure

```
├── main.py              # Core scraping logic and Flask API
├── streamlit_app.py     # Streamlit web interface
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── README.md           # This file
└── task.txt            # Original task requirements
```

## Key Components

### 1. Connectors
- **Amazon US**: Web scraping with anti-detection measures
- **Amazon India**: Selenium-based scraping for robust results
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
- Selenium with explicit waits

## Configuration

### Adding New Countries
Edit the `SITE_MAP` in `main.py`:
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

### Common Issues

1. **Chrome WebDriver issues**
   ```bash
   # Kill existing Chrome processes
   pkill -f chrome
   pkill -f chromedriver
   ```

2. **Selenium timeout**
   - Check internet connection
   - Increase wait times in the code
   - Check for CAPTCHA (screenshots saved automatically)

3. **No results found**
   - Verify the query format
   - Check if the product exists on the sites
   - Review debug logs

### Debug Mode
The application includes comprehensive logging. Check the terminal output for detailed information about:
- Number of products found
- Matching results
- Best prices from each site
- Any errors encountered

## Performance Notes

- **Response time**: 5-15 seconds depending on the number of sites
- **Rate limiting**: Built-in delays to avoid being blocked
- **Caching**: No caching implemented (can be added for production)

## Future Enhancements

1. **Real-time price tracking**
2. **Price history and trends**
3. **More retailers and countries**
4. **Advanced AI matching**
5. **Price alerts**
6. **Mobile app**

## License

This project is developed for educational and demonstration purposes.

## Support

For issues and questions, please check the troubleshooting section or create an issue in the repository. 
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Callable
import json
import re
import time
import random
from urllib.parse import urljoin, urlparse
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from flask import Flask, request, jsonify

# -------------------------------------------
# CONFIG
# -------------------------------------------

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SITE_MAP = {
    "US": ["Amazon", "Walmart"],
    "IN": ["AmazonIN", "Flipkart"]
}

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
]

REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 2

# -------------------------------------------
# UTILITY FUNCTIONS
# -------------------------------------------

def get_random_user_agent() -> str:
    return random.choice(USER_AGENTS)

def random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0):
    time.sleep(random.uniform(min_seconds, max_seconds))

def clean_price(price_text: str) -> Optional[str]:
    if not price_text:
        return None
    cleaned = re.sub(r'[^\d.,]', '', price_text.strip())
    if ',' in cleaned and '.' in cleaned:
        return cleaned.replace(',', '')
    elif ',' in cleaned:
        return cleaned.replace(',', '')
    else:
        return cleaned

def extract_price_from_element(element) -> Optional[str]:
    if not element:
        return None
    price_text = element.get_text(strip=True)
    if not price_text:
        price_text = element.get('content', '')
    return clean_price(price_text)

def normalize_query(query: str) -> str:
    return re.sub(r'[^\w\s]', '', query.lower()).strip()

def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

# -------------------------------------------
# CONNECTORS (MODULAR)
# -------------------------------------------

def make_request_with_retry(url: str, max_retries: int = MAX_RETRIES, headers: Optional[Dict] = None) -> Optional[requests.Response]:
    if headers is None:
        headers = {
            "User-Agent": get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
    for attempt in range(max_retries):
        try:
            logger.info(f"Making request to {url} (attempt {attempt + 1}/{max_retries})")
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)
            response.raise_for_status()
            if 'text/html' not in response.headers.get('content-type', ''):
                logger.warning(f"Non-HTML response received: {response.headers.get('content-type')}")
                continue
            return response
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                delay = RETRY_DELAY * (2 ** attempt)
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error(f"All retry attempts failed for {url}")
                return None
    return None

# --- Amazon US Connector ---
def search_amazon_us(query: str) -> List[Dict]:
    url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    response = make_request_with_retry(url, headers=headers)
    if not response:
        logger.error("Failed to fetch Amazon US results")
        return []
    soup = BeautifulSoup(response.content, 'html.parser')
    results = []
    items = soup.select('.s-result-item[data-component-type="s-search-result"]')
    logger.info(f"Found {len(items)} product items on Amazon US")
    for item in items[:20]:  # Limit to first 20 results
        try:
            title_elem = item.select_one('h2 span') or item.select_one('.a-size-medium') or item.select_one('.a-size-base-plus')
            if not title_elem:
                continue
            title = title_elem.get_text(strip=True)
            if not title:
                continue
            link_elem = item.select_one('h2 a') or item.select_one('a[href*="/dp/"]')
            if not link_elem or not link_elem.get('href'):
                continue
            href = link_elem.get('href')
            url = urljoin("https://www.amazon.com", href) if href.startswith('/') else href
            if not is_valid_url(url):
                continue
            price_elem = item.select_one(".a-price-whole") or item.select_one(".a-price .a-offscreen")
            price = extract_price_from_element(price_elem)
            if not price:
                price_pattern = r'\$[\d,]+(?:\.\d{2})?'
                price_match = re.search(price_pattern, item.get_text())
                if price_match:
                    price = clean_price(price_match.group())
            logger.info(f"EXTRACTED: {title} | {url} | {price}")
            if price:
                results.append({
                    "title": title,
                    "url": url,
                    "price": price,
                    "currency": "USD"
                })
        except Exception as e:
            logger.warning(f"Error processing product item: {e}")
            continue
    logger.info(f"Successfully extracted {len(results)} products from Amazon US")
    return results

# --- Amazon India Connector ---
def search_amazon_in(query: str) -> List[Dict]:
    search_url = f"https://www.amazon.in/s?k={requests.utils.quote(query)}"
    response = make_request_with_retry(search_url)
    if not response:
        logger.error("Failed to fetch Amazon India search results")
        return []
    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    product_selectors = [
        ".s-result-item[data-component-type='s-search-result']",
        ".s-result-item",
        "[data-asin]",
        ".sg-col-inner .s-result-item"
    ]
    for selector in product_selectors:
        items = soup.select(selector)
        if items:
            logger.info(f"Found {len(items)} products using selector: {selector}")
            break
    else:
        logger.warning("No products found with any selector")
        return []
    for item in items[:10]:
        try:
            title_elem = item.select_one("h2 span") or item.select_one(".a-size-medium")
            if not title_elem:
                continue
            title = title_elem.get_text(strip=True)
            link_elem = item.select_one("h2 a") or item.select_one(".a-link-normal[href*='/dp/']")
            if not link_elem or not link_elem.get('href'):
                continue
            href = link_elem.get('href')
            url = urljoin("https://www.amazon.in", href) if href.startswith('/') else href
            if not is_valid_url(url):
                continue
            price_elem = item.select_one(".a-price-whole") or item.select_one(".a-price .a-offscreen")
            price = extract_price_from_element(price_elem)
            if not price:
                price_pattern = r'₹[\d,]+(?:\.\d{2})?'
                price_match = re.search(price_pattern, item.get_text())
                if price_match:
                    price = clean_price(price_match.group())
            logger.info(f"EXTRACTED: {title} | {url} | {price}")
            if price:
                results.append({
                    "title": title,
                    "url": url,
                    "price": price,
                    "currency": "INR"
                })
        except Exception as e:
            logger.warning(f"Error processing product item: {e}")
            continue
    logger.info(f"Successfully extracted {len(results)} products from Amazon India")
    return results

def search_amazon_in_selenium(query: str) -> List[Dict]:
    url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Commented out for manual inspection
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    print('Page title:', driver.title)
    wait = WebDriverWait(driver, 30)  # Increased wait time
    results = []
    # CAPTCHA detection
    if "captcha" in driver.page_source.lower():
        print("CAPTCHA detected! Please solve it manually in the opened browser window.")
        driver.save_screenshot('amazon_captcha.png')
        print('Saved screenshot as amazon_captcha.png')
        driver.quit()
        return []
    # Wait for product elements to load
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".s-result-item[data-component-type='s-search-result']")))
    except Exception as e:
        print("Timeout waiting for product results.")
        driver.save_screenshot('amazon_timeout.png')
        print('Saved screenshot as amazon_timeout.png')
        driver.quit()
        return []
    # Scroll to load more results
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(3):  # Scroll 3 times
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    items = driver.find_elements(By.CSS_SELECTOR, ".s-result-item[data-component-type='s-search-result']")
    print('Number of product elements found:', len(items))
    if len(items) == 0:
        driver.save_screenshot('amazon_no_products.png')
        print('Saved screenshot as amazon_no_products.png')
    for item in items[:20]:  # Try to get up to 20 results
        try:
            # Updated selectors for title, link, price
            title_elem = None
            for sel in ["h2 span", ".a-size-medium", ".a-size-base-plus"]:
                try:
                    title_elem = item.find_element(By.CSS_SELECTOR, sel)
                    if title_elem:
                        break
                except:
                    continue
            if not title_elem:
                continue
            title = title_elem.text.strip()
            link_elem = None
            for sel in ["h2 a", ".a-link-normal[href*='/dp/']", "a[href*='/dp/']"]:
                try:
                    link_elem = item.find_element(By.CSS_SELECTOR, sel)
                    if link_elem and link_elem.get_attribute("href"):
                        break
                except:
                    continue
            if not link_elem:
                continue
            link = link_elem.get_attribute("href")
            price = None
            for sel in [".a-price-whole", ".a-price .a-offscreen", ".a-price-current .a-offscreen", "[data-a-color='price'] .a-offscreen", ".a-price-range .a-offscreen", ".a-price .a-price-symbol + span"]:
                try:
                    price_elem = item.find_element(By.CSS_SELECTOR, sel)
                    price = price_elem.text.replace(",", "").strip()
                    if price:
                        break
                except:
                    continue
            if not price:
                # Try to find any price-like text
                import re
                price_pattern = r'₹[\d,]+(?:\.\d{2})?'
                price_match = re.search(price_pattern, item.text)
                if price_match:
                    price = price_match.group().replace(",", "").replace("₹", "").strip()
            if title and link and price:
                print(f'Found product: {title} | {link} | {price}')
                results.append({
                    "title": title,
                    "url": link,
                    "price": price,
                    "currency": "INR"
                })
        except Exception as e:
            continue
    driver.quit()
    return results

# --- Flipkart India Connector (Mocked) ---
def search_flipkart_in(query: str) -> List[Dict]:
    # In a real implementation, you would scrape or use an API. Here, we mock for demo.
    logger.info(f"Mocked Flipkart search for: {query}")
    if "boAt Airdopes 311 Pro".lower() in query.lower():
        return [{
            "title": "boAt Airdopes 311 Pro True Wireless Earbuds",
            "url": "https://www.flipkart.com/boat-airdopes-311-pro/p/itm123456",
            "price": "999",
            "currency": "INR"
        }]
    return []

# --- Walmart US Connector (Mocked) ---
def search_walmart_us(query: str) -> List[Dict]:
    logger.info(f"Mocked Walmart search for: {query}")
    if "iPhone 16 Pro".lower() in query.lower():
        return [{
            "title": "Apple iPhone 16 Pro 128GB",
            "url": "https://www.walmart.com/ip/Apple-iPhone-16-Pro-128GB/123456789",
            "price": "999",
            "currency": "USD"
        }]
    elif "boAt Airdopes 311 Pro".lower() in query.lower():
        return [{
            "title": "boAt Airdopes 311 Pro True Wireless Earbuds",
            "url": "https://www.walmart.com/ip/boAt-Airdopes-311-Pro/987654321",
            "price": "49.99",
            "currency": "USD"
        }]
    return []

# --- Connector Registry ---
CONNECTORS: Dict[str, Callable[[str], List[Dict]]] = {
    "Amazon": search_amazon_us,
    "AmazonIN": search_amazon_in_selenium,
    "Flipkart": search_flipkart_in,
    "Walmart": search_walmart_us
}

def get_connector(site: str):
    if site not in CONNECTORS:
        raise ValueError(f"No connector defined for {site}")
    return CONNECTORS[site]

# -------------------------------------------
# LLM-based product matcher (placeholder for LLM integration)
# -------------------------------------------
def llm_product_match(query: str, title: str) -> bool:
    if not query or not title:
        return False
    normalized_query = normalize_query(query)
    normalized_title = normalize_query(title)
    query_words = set(normalized_query.split())
    title_words = set(normalized_title.split())
    if not query_words:
        return False
    matching_words = query_words.intersection(title_words)
    return len(matching_words) > 0

# -------------------------------------------
# AGGREGATOR
# -------------------------------------------
def fetch_prices(country: str, query: str) -> List[Dict]:
    if not query or not query.strip():
        logger.error("Empty query provided")
        return []
    websites = SITE_MAP.get(country, [])
    if not websites:
        logger.error(f"No websites configured for country: {country}")
        return []
    best_results = []
    for site in websites:
        logger.info(f"Searching {site} for '{query}'...")
        try:
            connector = get_connector(site)
            random_delay(1.0, 2.0)
            raw_results = connector(query)
            if not raw_results:
                logger.warning(f"No results found on {site}")
                continue
            logger.info(f"Found {len(raw_results)} raw results from {site}")
            matched_results = []
            for item in raw_results:
                if llm_product_match(query, item["title"]):
                    matched_results.append({
                        "link": item["url"],
                        "price": item["price"],
                        "currency": item["currency"],
                        "productName": item["title"],
                        "source": site
                    })
            logger.info(f"Matched {len(matched_results)} products from {site}")
            
            # Get the best (lowest price) result from this site
            if matched_results:
                def safe_price_sort(item):
                    try:
                        price_str = str(item["price"]).replace(",", "").replace("$", "").replace("₹", "")
                        return float(price_str)
                    except (ValueError, TypeError):
                        return float('inf')
                best_result = min(matched_results, key=safe_price_sort)
                best_results.append(best_result)
                logger.info(f"Best result from {site}: {best_result['productName']} at {best_result['price']} {best_result['currency']}")
        except Exception as e:
            logger.error(f"Error fetching from {site}: {e}")
            continue
    logger.info(f"Total results from {len(best_results)} sites")
    return best_results

# -------------------------------------------
# ENTRY POINT
# -------------------------------------------
app = Flask(__name__)

@app.route('/fetch_prices', methods=['POST'])
def api_fetch_prices():
    data = request.get_json()
    country = data.get('country')
    query = data.get('query')
    results = fetch_prices(country, query)
    # Return the best result from each site
    output = [
        {
            "link": r["link"],
            "price": r["price"],
            "currency": r["currency"],
            "productName": r["productName"],
            "source": r.get("source", "")
        }
        for r in results
    ]
    return jsonify(output)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        app.run(host="0.0.0.0", port=5000, debug=True)
    else:
        example_inputs = [
            {"country": "US", "query": "iPhone 16 Pro, 128GB"},
            {"country": "IN", "query": "boAt Airdopes 311 Pro"}
        ]
        for input_obj in example_inputs:
            country = input_obj["country"]
            query = input_obj["query"]
            print(f"\n{'='*60}")
            print(f"Results for {query} in {country}:")
            print(f"{'='*60}")
            try:
                results = fetch_prices(country, query)
                output = [
                    {
                        "link": r["link"],
                        "price": r["price"],
                        "currency": r["currency"],
                        "productName": r["productName"],
                        "source": r.get("source", "")
                    }
                    for r in results
                ]
                print(json.dumps(output, indent=2))
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                print(f"An error occurred: {e}")

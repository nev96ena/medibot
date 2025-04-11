import requests
from bs4 import BeautifulSoup
import random
import os
import time
import re
from urllib.parse import urljoin

INDEX_URL = 'https://medlineplus.gov/all_healthtopics.html'
BASE_URL = 'https://medlineplus.gov'
OUTPUT_DIR = '../data/med_articles/'
NUM_ARTICLES_TO_SCRAPE = 2500
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
REQUEST_DELAY = 1
REQUEST_TIMEOUT = 20


def discover_topic_urls(index_url, base_url):
    topic_urls = set()
    try:
        response = requests.get(index_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        link_elements = soup.select('div.az-results ul li a')
        if not link_elements:
            link_elements = soup.select('#index ul li a')
        if not link_elements:
            link_elements = soup.find_all('a', href=True)
        for link in link_elements:
            href = link.get('href')
            if href and not href.startswith('#') and not href.startswith('javascript:'):
                full_url = urljoin(base_url, href)
                if full_url.startswith(base_url) and ('.html' in href or '/ency/' in href or '/topic/' in href):
                    if '/all_healthtopics.html' not in full_url and '/healthtopics.html' not in full_url and full_url != base_url + '/':
                        topic_urls.add(full_url)
        return list(topic_urls)
    except requests.exceptions.HTTPError as http_err:
        print(f"Error accessing index page {index_url}: {http_err}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Network/timeout error accessing {index_url}: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error processing {index_url}: {e}")
        return []


def scrape_summary(url):
    try:
        time.sleep(REQUEST_DELAY)
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        summary_div = soup.find('div', id='topic-summary')
        if summary_div:
            summary_text = summary_div.get_text(separator=' ', strip=True)
            if summary_text:
                return summary_text
            else:
                return None
        else:
            return None
    except requests.exceptions.Timeout:
        print(f"Timeout error for {url}")
        return None
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error for {url}: {http_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Network error for {url}: {req_err}")
        return None
    except Exception as e:
        print(f"Unexpected error processing {url}: {e}")
        return None


def clean_filename(url):
    try:
        name = url.split('/')[-1]
        name = re.sub(r'\.(html|htm)$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'[^\w\-]+', '_', name)
        name = re.sub(r'_+', '_', name).strip('_')
        if not name:
            name = re.sub(r'[^\w\-]+', '_', url.replace(BASE_URL, '').strip('/'))
            name = re.sub(r'_+', '_', name).strip('_')[:50]
        return name if name else f"unknown_topic_{random.randint(1000,9999)}"
    except Exception:
        return f"topic_{random.randint(10000, 99999)}"


def save_summary(summary, url, output_dir):
    filename_base = clean_filename(url)
    filepath = os.path.join(output_dir, f"{filename_base}.txt")
    try:
        os.makedirs(output_dir, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(summary)
        return True
    except IOError as e:
        print(f"Error saving file {filepath}: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error saving {filepath}: {e}")
        return False


if __name__ == "__main__":
    all_topic_urls = discover_topic_urls(INDEX_URL, BASE_URL)
    if not all_topic_urls:
        print("No topic URLs found. Exiting.")
        exit()
    num_available = len(all_topic_urls)
    num_to_process = min(NUM_ARTICLES_TO_SCRAPE, num_available)
    if num_available < NUM_ARTICLES_TO_SCRAPE:
        print(f"Warning: Found only {num_available} URLs, processing all available.")
    else:
        print(f"Found {num_available} URLs. Randomly selecting {num_to_process}.")
    random.shuffle(all_topic_urls)
    selected_urls = all_topic_urls[:num_to_process]
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    success_count = 0
    fail_count = 0
    print(f"Starting to download {num_to_process}")
    for i, url in enumerate(selected_urls, 1):
        print(f"\n[{i}/{num_to_process}] Processing URL:")
        summary_text = scrape_summary(url)
        if summary_text:
            if save_summary(summary_text, url, OUTPUT_DIR):
                success_count += 1
            else:
                fail_count += 1
        else:
            fail_count += 1
    print("\n--- Download complete ---")
    print(f"Successfully downloaded and saved: {success_count}")

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import json
import sqlite3
from urllib.parse import urljoin, urlparse
import time
import logging
from typing import List, Dict
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

class WebScraper:
    """
    Advanced web scraper with data extraction, storage, and analytics capabilities.
    """
    
    def __init__(self, db_name='scraper_data.db'):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.db_name = db_name
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for storing scraped data."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraped_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT,
                content TEXT,
                metadata TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraping_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                total_pages INTEGER,
                successful INTEGER,
                failed INTEGER,
                duration REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logging.info("Database initialized successfully")
    
    def fetch_page(self, url: str, timeout: int = 10) -> requests.Response:
        """Fetch a web page with error handling."""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            logging.info(f"Successfully fetched: {url}")
            return response
        except requests.RequestException as e:
            logging.error(f"Error fetching {url}: {str(e)}")
            raise
    
    def extract_text(self, soup: BeautifulSoup) -> str:
        """Extract clean text from HTML."""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        return text
    
    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all links from a page."""
        links = []
        for link in soup.find_all('a', href=True):
            url = urljoin(base_url, link['href'])
            if urlparse(url).netloc == urlparse(base_url).netloc:
                links.append(url)
        return list(set(links))
    
    def extract_metadata(self, soup: BeautifulSoup) -> Dict:
        """Extract metadata from page."""
        metadata = {
            'description': '',
            'keywords': '',
            'author': '',
            'og_title': '',
            'og_description': ''
        }
        
        # Meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', '').lower()
            property = meta.get('property', '').lower()
            content = meta.get('content', '')
            
            if name == 'description':
                metadata['description'] = content
            elif name == 'keywords':
                metadata['keywords'] = content
            elif name == 'author':
                metadata['author'] = content
            elif property == 'og:title':
                metadata['og_title'] = content
            elif property == 'og:description':
                metadata['og_description'] = content
        
        return metadata
    
    def scrape_page(self, url: str) -> Dict:
        """Scrape a single page and extract data."""
        try:
            response = self.fetch_page(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            data = {
                'url': url,
                'title': soup.title.string if soup.title else '',
                'content': self.extract_text(soup),
                'links': self.extract_links(soup, url),
                'metadata': self.extract_metadata(soup),
                'status': 'success'
            }
            
            return data
            
        except Exception as e:
            logging.error(f"Error scraping {url}: {str(e)}")
            return {
                'url': url,
                'title': '',
                'content': '',
                'links': [],
                'metadata': {},
                'status': 'failed'
            }
    
    def save_to_db(self, data: Dict):
        """Save scraped data to database."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO scraped_data (url, title, content, metadata, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data['url'],
            data['title'],
            data['content'],
            json.dumps(data['metadata']),
            data['status']
        ))
        
        conn.commit()
        conn.close()
    
    def scrape_multiple(self, urls: List[str], delay: float = 1.0) -> List[Dict]:
        """Scrape multiple URLs with delay between requests."""
        results = []
        session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        start_time = time.time()
        successful = 0
        failed = 0
        
        for i, url in enumerate(urls, 1):
            logging.info(f"Scraping {i}/{len(urls)}: {url}")
            
            data = self.scrape_page(url)
            results.append(data)
            self.save_to_db(data)
            
            if data['status'] == 'success':
                successful += 1
            else:
                failed += 1
            
            if i < len(urls):
                time.sleep(delay)
        
        duration = time.time() - start_time
        
        # Save statistics
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO scraping_stats (session_id, total_pages, successful, failed, duration)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, len(urls), successful, failed, duration))
        conn.commit()
        conn.close()
        
        logging.info(f"Scraping completed: {successful} successful, {failed} failed, {duration:.2f}s")
        return results
    
    def get_statistics(self) -> pd.DataFrame:
        """Get scraping statistics."""
        conn = sqlite3.connect(self.db_name)
        df = pd.read_sql_query("SELECT * FROM scraping_stats", conn)
        conn.close()
        return df
    
    def export_to_csv(self, filename: str = 'scraped_data.csv'):
        """Export scraped data to CSV."""
        conn = sqlite3.connect(self.db_name)
        df = pd.read_sql_query("SELECT * FROM scraped_data", conn)
        conn.close()
        df.to_csv(filename, index=False)
        logging.info(f"Data exported to {filename}")
    
    def export_to_json(self, filename: str = 'scraped_data.json'):
        """Export scraped data to JSON."""
        conn = sqlite3.connect(self.db_name)
        df = pd.read_sql_query("SELECT * FROM scraped_data", conn)
        conn.close()
        df.to_json(filename, orient='records', indent=2)
        logging.info(f"Data exported to {filename}")
    
    def analyze_content(self) -> Dict:
        """Analyze scraped content."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Get basic statistics
        cursor.execute("SELECT COUNT(*) FROM scraped_data WHERE status='success'")
        total_successful = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM scraped_data WHERE status='failed'")
        total_failed = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(LENGTH(content)) FROM scraped_data WHERE status='success'")
        avg_content_length = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_pages': total_successful + total_failed,
            'successful': total_successful,
            'failed': total_failed,
            'success_rate': (total_successful / (total_successful + total_failed) * 100) if (total_successful + total_failed) > 0 else 0,
            'avg_content_length': round(avg_content_length, 2)
        }


def main():
    """Example usage of the WebScraper."""
    scraper = WebScraper()
    
    # Example URLs to scrape
    urls = [
        'https://example.com',
        'https://example.com/about',
        'https://example.com/contact'
    ]
    
    print("Starting web scraping...")
    results = scraper.scrape_multiple(urls, delay=2.0)
    
    print("\n=== Scraping Results ===")
    for result in results:
        print(f"URL: {result['url']}")
        print(f"Status: {result['status']}")
        print(f"Title: {result['title']}")
        print(f"Content length: {len(result['content'])} characters")
        print("-" * 50)
    
    print("\n=== Analytics ===")
    analysis = scraper.analyze_content()
    for key, value in analysis.items():
        print(f"{key}: {value}")
    
    # Export data
    scraper.export_to_csv()
    scraper.export_to_json()
    
    print("\nData exported successfully!")


if __name__ == "__main__":
    main()
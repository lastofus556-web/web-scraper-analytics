import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
from wordcloud import WordCloud
import seaborn as sns
from collections import Counter
import re
from urllib.parse import urlparse

class DataVisualizer:
    """Visualize scraped data with charts and analytics."""
    
    def __init__(self, db_name='scraper_data.db'):
        self.db_name = db_name
        sns.set_style('whitegrid')
    
    def load_data(self) -> pd.DataFrame:
        """Load data from database."""
        conn = sqlite3.connect(self.db_name)
        df = pd.read_sql_query("SELECT * FROM scraped_data", conn)
        conn.close()
        return df
    
    def plot_success_rate(self):
        """Plot success vs failed scraping attempts."""
        df = self.load_data()
        status_counts = df['status'].value_counts()
        
        plt.figure(figsize=(10, 6))
        colors = ['#2ecc71', '#e74c3c']
        plt.pie(status_counts.values, labels=status_counts.index, 
                autopct='%1.1f%%', startangle=90, colors=colors)
        plt.title('Scraping Success Rate', fontsize=16, fontweight='bold')
        plt.savefig('success_rate.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Success rate chart saved: success_rate.png")
    
    def plot_content_length_distribution(self):
        """Plot distribution of content lengths."""
        df = self.load_data()
        df['content_length'] = df['content'].str.len()
        
        plt.figure(figsize=(12, 6))
        plt.hist(df['content_length'], bins=30, color='#3498db', edgecolor='black')
        plt.xlabel('Content Length (characters)', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.title('Distribution of Content Lengths', fontsize=16, fontweight='bold')
        plt.grid(alpha=0.3)
        plt.savefig('content_length_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Content length distribution saved: content_length_distribution.png")
    
    def plot_scraping_timeline(self):
        """Plot scraping activity over time."""
        conn = sqlite3.connect(self.db_name)
        df = pd.read_sql_query("SELECT * FROM scraping_stats", conn)
        conn.close()
        
        if df.empty:
            print("No scraping statistics available")
            return
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        plt.figure(figsize=(14, 6))
        plt.plot(df['timestamp'], df['total_pages'], marker='o', 
                linewidth=2, markersize=8, color='#9b59b6')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Pages Scraped', fontsize=12)
        plt.title('Scraping Activity Timeline', fontsize=16, fontweight='bold')
        plt.xticks(rotation=45)
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig('scraping_timeline.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Timeline chart saved: scraping_timeline.png")
    
    def generate_wordcloud(self):
        """Generate word cloud from scraped content."""
        df = self.load_data()
        text = ' '.join(df['content'].dropna())
        
        # Remove common words and clean text
        text = re.sub(r'[^\w\s]', '', text.lower())
        
        wordcloud = WordCloud(width=1600, height=800, 
                            background_color='white',
                            colormap='viridis',
                            max_words=100).generate(text)
        
        plt.figure(figsize=(16, 8))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Most Common Words in Scraped Content', 
                fontsize=20, fontweight='bold', pad=20)
        plt.savefig('wordcloud.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Word cloud saved: wordcloud.png")
    
    def plot_top_domains(self, top_n=10):
        """Plot top scraped domains."""
        df = self.load_data()
        
        df['domain'] = df['url'].apply(lambda x: urlparse(x).netloc)
        domain_counts = df['domain'].value_counts().head(top_n)
        
        plt.figure(figsize=(12, 6))
        domain_counts.plot(kind='barh', color='#1abc9c')
        plt.xlabel('Number of Pages', fontsize=12)
        plt.ylabel('Domain', fontsize=12)
        plt.title(f'Top {top_n} Scraped Domains', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig('top_domains.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Top domains chart saved: top_domains.png")
    
    def generate_summary_report(self):
        """Generate a comprehensive summary report."""
        df = self.load_data()
        
        report = f"""
╔══════════════════════════════════════════════════════╗
║          WEB SCRAPER ANALYTICS REPORT                ║
╚══════════════════════════════════════════════════════╝

📊 GENERAL STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Pages Scraped:        {len(df)}
Successful Scrapes:         {len(df[df['status'] == 'success'])}
Failed Scrapes:             {len(df[df['status'] == 'failed'])}
Success Rate:               {len(df[df['status'] == 'success'])/len(df)*100:.2f}%

📝 CONTENT STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Avg Content Length:         {df['content'].str.len().mean():.0f} characters
Max Content Length:         {df['content'].str.len().max():.0f} characters
Min Content Length:         {df['content'].str.len().min():.0f} characters

🌐 DOMAIN STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Unique Domains:             {df['url'].apply(lambda x: urlparse(x).netloc).nunique()}

⏱️  LATEST SCRAPING SESSION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Last Scrape:                {df['timestamp'].max()}

"""
        print(report)
        
        with open('scraping_report.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        print("✓ Summary report saved: scraping_report.txt")
    
    def generate_all_visualizations(self):
        """Generate all visualizations at once."""
        print("\n🎨 Generating visualizations...\n")
        
        self.plot_success_rate()
        self.plot_content_length_distribution()
        self.plot_scraping_timeline()
        self.generate_wordcloud()
        self.plot_top_domains()
        self.generate_summary_report()
        
        print("\n✅ All visualizations generated successfully!")


def main():
    visualizer = DataVisualizer()
    visualizer.generate_all_visualizations()


if __name__ == "__main__":
    main()
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

# 🕷️ Advanced Web Scraper & Analytics

Профессиональный веб-скрапер с автоматическим сбором данных, аналитикой и визуализацией.

## ✨ Возможности

- **Умное извлечение контента**: текст, заголовки, метаданные
- **SQLite база данных**: эффективное хранение данных
- **Экспорт в CSV/JSON**: поддержка популярных форматов
- **Визуализация**: графики, word cloud, отчёты
- **Аналитика**: детальная статистика скрапинга

## 🚀 Установка

\`\`\`bash
git clone https://github.com/lastofus556-web/web-scraper-analytics.git
cd web-scraper-analytics

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
\`\`\`

## 📖 Использование

### Базовый скрапинг

\`\`\`python
from scraper import WebScraper

scraper = WebScraper()
urls = ['https://example.com', 'https://example.com/about']
results = scraper.scrape_multiple(urls, delay=2.0)
\`\`\`

### Визуализация

\`\`\`python
from visualizer import DataVisualizer

visualizer = DataVisualizer()
visualizer.generate_all_visualizations()
\`\`\`

## 📝 Лицензия

MIT License

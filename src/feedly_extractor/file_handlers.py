"""File handling and export functionality."""

import csv
import json
import os
from typing import List, Dict, Any

from .models import Article


class FileHandler:
    """Handles saving articles in various formats."""
    
    @staticmethod
    def save_to_csv(articles: List[Article], filename: str) -> None:
        """Save articles to CSV file"""
        if not articles:
            print("⚠️ No articles to save")
            return

        article_dicts = [article.to_dict() for article in articles]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = article_dicts[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for article_dict in article_dicts:
                writer.writerow(article_dict)

        print(f"💾 Saved {len(articles)} articles to {filename}")
    
    @staticmethod
    def init_csv_file(filename: str, fieldnames: List[str]) -> None:
        """Initialize CSV file with headers"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
    
    @staticmethod
    def append_to_csv(articles: List[Article], filename: str) -> None:
        """Append articles to existing CSV file"""
        if not articles:
            return
        
        article_dicts = [article.to_dict() for article in articles]
            
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = article_dicts[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            for article_dict in article_dicts:
                writer.writerow(article_dict)

    @staticmethod
    def save_to_json(articles: List[Article], filename: str) -> None:
        """Save articles to JSON file"""
        article_dicts = [article.to_dict() for article in articles]
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(article_dicts, jsonfile, indent=2, ensure_ascii=False)

        print(f"💾 Saved {len(articles)} articles to {filename}")

    @staticmethod
    def save_urls_only(articles: List[Article], filename: str) -> None:
        """Save only URLs to a text file"""
        urls = [article.url for article in articles if article.url]

        with open(filename, 'w', encoding='utf-8') as urlfile:
            for url in urls:
                urlfile.write(url + '\n')

        print(f"🔗 Saved {len(urls)} URLs to {filename}")
    
    @staticmethod
    def append_urls(articles: List[Article], filename: str) -> None:
        """Append URLs to existing text file"""
        urls = [article.url for article in articles if article.url]
        if not urls:
            return
            
        with open(filename, 'a', encoding='utf-8') as urlfile:
            for url in urls:
                urlfile.write(url + '\n')


class ProgressiveSaver:
    """Handles progressive saving of articles as they're fetched."""
    
    def __init__(self, output_prefix: str, output_format: str):
        self.output_prefix = output_prefix
        self.output_format = output_format
        self.csv_file = f"{output_prefix}.csv" if output_format in ['all', 'csv'] else None
        self.json_file = f"{output_prefix}.json" if output_format in ['all', 'json'] else None
        self.urls_file = f"{output_prefix}_urls.txt" if output_format in ['all', 'urls'] else None
        self.files_initialized = False
        self.saved_count = 0
        
        # Initialize files
        self._initialize_files()
    
    def _initialize_files(self) -> None:
        """Initialize output files"""
        if self.csv_file:
            open(self.csv_file, 'w').close()
        if self.json_file:
            with open(self.json_file, 'w') as f:
                f.write('[\n')  # Start JSON array
        if self.urls_file:
            open(self.urls_file, 'w').close()
    
    def save_batch(self, articles: List[Article], quiet: bool = False) -> None:
        """Save a batch of articles progressively"""
        if not articles:
            return
        
        # Initialize CSV headers if needed
        if self.csv_file and not self.files_initialized:
            FileHandler.init_csv_file(self.csv_file, list(articles[0].to_dict().keys()))
            self.files_initialized = True
        
        # Save batch to each format
        if self.csv_file:
            FileHandler.append_to_csv(articles, self.csv_file)
        if self.urls_file:
            FileHandler.append_urls(articles, self.urls_file)
        if self.json_file:
            self._append_to_json(articles)
        
        self.saved_count += len(articles)
        
        if not quiet:
            print(f"   💾 Saved batch: {len(articles)} articles (total saved: {self.saved_count})")
    
    def _append_to_json(self, articles: List[Article]) -> None:
        """Append articles to JSON file"""
        with open(self.json_file, 'a') as f:
            for i, article in enumerate(articles):
                if self.saved_count > 0 or i > 0:
                    f.write(',\n')
                json.dump(article.to_dict(), f, indent=2, ensure_ascii=False)
    
    def finalize(self, quiet: bool = False) -> None:
        """Finalize progressive saving"""
        # Close JSON array
        if self.json_file and self.saved_count > 0:
            with open(self.json_file, 'a') as f:
                f.write('\n]')  # End JSON array
        
        if self.saved_count > 0 and not quiet:
            print(f"\n✅ Progressive save complete: {self.saved_count} articles saved")
            if self.csv_file:
                print(f"   📄 CSV: {self.csv_file}")
            if self.json_file:
                print(f"   📄 JSON: {self.json_file}")
            if self.urls_file:
                print(f"   📄 URLs: {self.urls_file}")
    
    @property
    def total_saved(self) -> int:
        """Get total number of articles saved"""
        return self.saved_count
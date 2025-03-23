#!/usr/bin/env python3
"""
Bunkr Scraper - Backend Module

This module provides functionality to scrape content from bunkr.cr with customizable parameters
including content type filtering, time period selection, and file size filtering.
"""

import os
import re
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

import requests
from bs4 import BeautifulSoup
import aiohttp
import asyncio
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("bunkr_scraper")

# Constants
BASE_URL = "https://bunkr.cr"
ALBUMS_URL = "https://bunkr-albums.io"
VIDEOS_URL = f"{ALBUMS_URL}/topvideos"
IMAGES_URL = f"{ALBUMS_URL}/topimages"
FILES_URL = f"{ALBUMS_URL}/topfiles"

# Time periods for filtering
TIME_PERIODS = ["24h", "7d", "30d", "all"]

class BunkrScraper:
    """Main scraper class for Bunkr website"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the scraper with configuration
        
        Args:
            config: Dictionary containing configuration parameters
                - min_size: Minimum file size in MB (default: 0)
                - max_size: Maximum file size in MB (default: None - no limit)
                - daily_download_limit: Maximum download size per day in MB (default: None - no limit)
                - daily_upload_limit: Maximum upload size per day in MB (default: None - no limit)
                - download_dir: Directory to save downloaded files (default: ./downloads)
                - content_types: List of content types to scrape (default: ["videos", "images", "files"])
                - time_period: Time period to filter content (default: "24h")
        """
        self.config = config or {}
        self.min_size = self.config.get("min_size", 0)  # MB
        self.max_size = self.config.get("max_size", None)  # MB, None means no limit
        self.daily_download_limit = self.config.get("daily_download_limit", None)  # MB, None means no limit
        self.daily_upload_limit = self.config.get("daily_upload_limit", None)  # MB, None means no limit
        self.download_dir = self.config.get("download_dir", "./downloads")
        self.content_types = self.config.get("content_types", ["videos", "images", "files"])
        self.time_period = self.config.get("time_period", "24h")
        
        # Create download directory if it doesn't exist
        os.makedirs(self.download_dir, exist_ok=True)
        
        # Usage tracking
        self.usage_file = "usage.json"
        self.usage = self._load_usage()
        
        # Session for requests
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        
        logger.info(f"Initialized BunkrScraper with config: {self.config}")
    
    def _load_usage(self) -> Dict:
        """Load usage data from file or create new if not exists"""
        if os.path.exists(self.usage_file):
            try:
                with open(self.usage_file, "r") as f:
                    usage = json.load(f)
                
                # Reset usage if it's a new day
                today = datetime.now().strftime("%Y-%m-%d")
                if usage.get("date") != today:
                    usage = {
                        "date": today,
                        "downloaded": 0,
                        "uploaded": 0
                    }
            except Exception as e:
                logger.error(f"Error loading usage data: {e}")
                usage = self._create_new_usage()
        else:
            usage = self._create_new_usage()
        
        return usage
    
    def _create_new_usage(self) -> Dict:
        """Create new usage tracking data"""
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "downloaded": 0,
            "uploaded": 0
        }
    
    def _save_usage(self):
        """Save usage data to file"""
        try:
            with open(self.usage_file, "w") as f:
                json.dump(self.usage, f)
        except Exception as e:
            logger.error(f"Error saving usage data: {e}")
    
    def _update_download_usage(self, size_mb: float):
        """Update download usage tracking"""
        self.usage["downloaded"] += size_mb
        self._save_usage()
    
    def _update_upload_usage(self, size_mb: float):
        """Update upload usage tracking"""
        self.usage["uploaded"] += size_mb
        self._save_usage()
    
    def _check_download_limit(self, size_mb: float) -> bool:
        """Check if download would exceed daily limit"""
        if self.daily_download_limit is None:
            return True
        
        return (self.usage["downloaded"] + size_mb) <= self.daily_download_limit
    
    def _check_upload_limit(self, size_mb: float) -> bool:
        """Check if upload would exceed daily limit"""
        if self.daily_upload_limit is None:
            return True
        
        return (self.usage["uploaded"] + size_mb) <= self.daily_upload_limit
    
    def _parse_size(self, size_text: str) -> float:
        """
        Parse file size from text (e.g., "24.9 MB")
        
        Args:
            size_text: Text containing file size
            
        Returns:
            Size in MB as float
        """
        try:
            match = re.search(r"([\d.]+)\s*([KMG]B)", size_text)
            if not match:
                return 0
            
            size, unit = match.groups()
            size = float(size)
            
            if unit == "KB":
                size /= 1024
            elif unit == "GB":
                size *= 1024
                
            return size
        except Exception as e:
            logger.error(f"Error parsing size '{size_text}': {e}")
            return 0
    
    def _filter_by_size(self, size_mb: float) -> bool:
        """
        Check if file size is within configured limits
        
        Args:
            size_mb: File size in MB
            
        Returns:
            True if file size is within limits, False otherwise
        """
        if size_mb < self.min_size:
            return False
        
        if self.max_size is not None and size_mb > self.max_size:
            return False
            
        return True
    
    async def scrape_videos(self) -> List[Dict]:
        """
        Scrape videos from Bunkr
        
        Returns:
            List of dictionaries containing video information
        """
        url = f"{VIDEOS_URL}?lapse={self.time_period}"
        logger.info(f"Scraping videos from {url}")
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            videos = []
            
            # Find all video elements
            video_elements = soup.find_all("a", {"aria-label": "watch"})
            
            for element in video_elements:
                # Get parent element which contains the video info
                parent = element.parent
                if not parent:
                    continue
                
                # Extract video name and size
                name_element = parent.find("div", text=lambda t: t and t.endswith(".mp4"))
                size_element = parent.find("div", text=lambda t: t and "MB" in t or "GB" in t)
                
                if not name_element or not size_element:
                    continue
                
                name = name_element.text.strip()
                size_text = size_element.text.strip()
                
                # Extract size in MB
                size_mb = self._parse_size(size_text)
                
                # Filter by size
                if not self._filter_by_size(size_mb):
                    continue
                
                # Extract video URL
                video_url = element.get("href")
                if video_url and not video_url.startswith("http"):
                    video_url = f"{ALBUMS_URL}{video_url}"
                
                videos.append({
                    "name": name,
                    "size": size_mb,
                    "size_text": size_text,
                    "url": video_url,
                    "type": "video"
                })
            
            logger.info(f"Found {len(videos)} videos matching criteria")
            return videos
            
        except Exception as e:
            logger.error(f"Error scraping videos: {e}")
            return []
    
    async def scrape_images(self) -> List[Dict]:
        """
        Scrape images from Bunkr
        
        Returns:
            List of dictionaries containing image information
        """
        url = f"{IMAGES_URL}?lapse={self.time_period}"
        logger.info(f"Scraping images from {url}")
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            images = []
            
            # Find all image elements
            image_elements = soup.find_all("a", {"aria-label": "watch"})
            
            for element in image_elements:
                # Get parent element which contains the image info
                parent = element.parent
                if not parent:
                    continue
                
                # Extract image name and size
                name_element = parent.find("div", text=lambda t: t and any(t.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif"]))
                size_element = parent.find("div", text=lambda t: t and "MB" in t or "KB" in t or "GB" in t)
                
                if not name_element or not size_element:
                    continue
                
                name = name_element.text.strip()
                size_text = size_element.text.strip()
                
                # Extract size in MB
                size_mb = self._parse_size(size_text)
                
                # Filter by size
                if not self._filter_by_size(size_mb):
                    continue
                
                # Extract image URL
                image_url = element.get("href")
                if image_url and not image_url.startswith("http"):
                    image_url = f"{ALBUMS_URL}{image_url}"
                
                images.append({
                    "name": name,
                    "size": size_mb,
                    "size_text": size_text,
                    "url": image_url,
                    "type": "image"
                })
            
            logger.info(f"Found {len(images)} images matching criteria")
            return images
            
        except Exception as e:
            logger.error(f"Error scraping images: {e}")
            return []
    
    async def scrape_files(self) -> List[Dict]:
        """
        Scrape files from Bunkr
        
        Returns:
            List of dictionaries containing file information
        """
        url = f"{FILES_URL}?lapse={self.time_period}"
        logger.info(f"Scraping files from {url}")
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            files = []
            
            # Find all file elements
            file_elements = soup.find_all("a", {"aria-label": "watch"})
            
            for element in file_elements:
                # Get parent element which contains the file info
                parent = element.parent
                if not parent:
                    continue
                
                # Extract file name and size
                name_element = parent.find("div", text=lambda t: t and "." in t)
                size_element = parent.find("div", text=lambda t: t and "MB" in t or "KB" in t or "GB" in t)
                
                if not name_element or not size_element:
                    continue
                
                name = name_element.text.strip()
                size_text = size_element.text.strip()
                
                # Extract size in MB
                size_mb = self._parse_size(size_text)
                
                # Filter by size
                if not self._filter_by_size(size_mb):
                    continue
                
                # Extract file URL
                file_url = element.get("href")
                if file_url and not file_url.startswith("http"):
                    file_url = f"{ALBUMS_URL}{file_url}"
                
                files.append({
                    "name": name,
                    "size": size_mb,
                    "size_text": size_text,
                    "url": file_url,
                    "type": "file"
                })
            
            logger.info(f"Found {len(files)} files matching criteria")
            return files
            
        except Exception as e:
            logger.error(f"Error scraping files: {e}")
            return []
    
    async def get_download_url(self, content_url: str) -> Optional[str]:
        """
        Get direct download URL for content
        
        Args:
            content_url: URL of content page
            
        Returns:
            Direct download URL or None if not found
        """
        try:
            response = self.session.get(content_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Find download button
            download_link = soup.find("a", text="Download")
            if download_link:
                download_url = download_link.get("href")
                if download_url:
                    if not download_url.startswith("http"):
                        download_url = f"{BASE_URL}{download_url}"
                    return download_url
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting download URL for {content_url}: {e}")
            return None
    
    async def download_file(self, url: str, filename: str, size_mb: float) -> bool:
        """
        Download file from URL
        
        Args:
            url: URL to download from
            filename: Name to save file as
            size_mb: Size of file in MB
            
        Returns:
            True if download successful, False otherwise
        """
        # Check if download would exceed daily limit
        if not self._check_download_limit(size_mb):
            logger.warning(f"Download of {filename} ({size_mb} MB) would exceed daily limit of {self.daily_download_limit} MB")
            return False
        
        filepath = os.path.join(self.download_dir, filename)
        
        try:
            # Download with progress bar
            with self.session.get(url, stream=True) as response:
                response.raise_for_status()
                total_size = int(response.headers.get("content-length", 0))
                
                with open(filepath, "wb") as f, tqdm(
                    desc=filename,
                    total=total_size,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                ) as progress:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            progress.update(len(chunk))
            
            # Update usage tracking
            self._update_download_usage(size_mb)
            
            logger.info(f"Downloaded {filename} ({size_mb} MB)")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading {url} to {filepath}: {e}")
            # Remove partial download if it exists
            if os.path.exists(filepath):
                os.remove(filepath)
            return False
    
    async def scrape_content(self) -> Dict[str, List[Dict]]:
        """
        Scrape content based on configuration
        
        Returns:
            Dictionary with content types as keys and lists of content items as values
        """
        results = {}
        
        if "videos" in self.content_types:
            results["videos"] = await self.scrape_videos()
        
        if "images" in self.content_types:
            results["images"] = await self.scrape_images()
        
        if "files" in self.content_types:
            results["files"] = await self.scrape_files()
        
        return results
    
    async def download_content(self, content_items: List[Dict]) -> Tuple[int, int]:
        """
        Download content items
        
        Args:
            content_items: List of content items to download
            
        Returns:
            Tuple of (successful downloads, failed downloads)
        """
        success_count = 0
        fail_count = 0
        
        for item in content_items:
            # Get direct download URL
            download_url = await self.get_download_url(item["url"])
            if not download_url:
                logger.warning(f"Could not get download URL for {item['name']}")
                fail_count += 1
                continue
            
            # Download file
            if await self.download_file(download_url, item["name"], item["size"]):
                success_count += 1
            else:
                fail_count += 1
        
        return success_count, fail_count
    
    def get_usage_stats(self) -> Dict:
        """
        Get current usage statistics
        
        Returns:
            Dictionary with usage statistics
        """
        return {
            "date": self.usage["date"],
            "downloaded": self.usage["downloaded"],
            "uploaded": self.usage["uploaded"],
            "download_limit": self.daily_download_limit,
            "upload_limit": self.daily_upload_limit,
            "download_remaining": None if self.daily_download_limit is None else max(0, self.daily_download_limit - self.usage["downloaded"]),
            "upload_remaining": None if self.daily_upload_limit is None else max(0, self.daily_upload_limit - self.usage["uploaded"])
        }
    
    def update_config(self, new_config: Dict):
        """
        Update scraper configuration
        
        Args:
            new_config: New configuration parameters
        """
        self.config.update(new_config)
        
        # Update instance variables
        if "min_size" in new_config:
            self.min_size = new_config["min_size"]
        if "max_size" in new_config:
            self.max_size = new_config["max_size"]
        if "daily_download_limit" in new_config:
            self.daily_download_limit = new_config["daily_download_limit"]
        if "daily_upload_limit" in new_config:
            self.daily_upload_limit = new_config["daily_upload_limit"]
        if "download_dir" in new_config:
            self.download_dir = new_config["download_dir"]
            os.makedirs(self.download_dir, exist_ok=True)
        if "content_types" in new_config:
            self.content_types = new_config["content_types"]
        if "time_period" in new_config:
            self.time_period = new_config["time_period"]
        
        logger.info(f"Updated configuration: {self.config}")

async def main():
    """Test function to demonstrate scraper usage"""
    # Example configuration
    config = {
        "min_size": 5,  # Minimum 5 MB
        "max_size": 500,  # Maximum 500 MB
        "daily_download_limit": 1000,  # 1 GB daily limit
        "daily_upload_limit": 1000,  # 1 GB daily limit
        "download_dir": "./downloads",
        "content_types": ["videos", "images", "files"],
        "time_period": "24h"
    }
    
    # Initialize scraper
    scraper = BunkrScraper(config)
    
    # Scrape content
    content = await scraper.scrape_content()
    
    # Print results
    for content_type, items in content.items():
        print(f"Found {len(items)} {content_type}")
        for item in items[:5]:  # Print first 5 items
            print(f"  - {item['name']} ({item['size_text']})")
    
    # Get usage stats
    usage = scraper.get_usage_stats()
    print(f"Usage stats: {usage}")

if __name__ == "__main__":
    asyncio.run(main())

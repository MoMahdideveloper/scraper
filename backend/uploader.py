#!/usr/bin/env python3
"""
Bunkr Scraper - Upload Module

This module provides functionality to upload downloaded content to a local project.
"""

import os
import shutil
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("uploader.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("bunkr_uploader")

class ContentUploader:
    """Content uploader class for managing uploads to local project"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the uploader with configuration
        
        Args:
            config: Dictionary containing configuration parameters
                - upload_dir: Directory to upload files to (default: ./uploads)
                - daily_upload_limit: Maximum upload size per day in MB (default: None - no limit)
        """
        self.config = config or {}
        self.upload_dir = self.config.get("upload_dir", "./uploads")
        self.daily_upload_limit = self.config.get("daily_upload_limit", None)
        
        # Create upload directory if it doesn't exist
        os.makedirs(self.upload_dir, exist_ok=True)
        
        # Create subdirectories for different content types
        self.video_dir = os.path.join(self.upload_dir, "videos")
        self.image_dir = os.path.join(self.upload_dir, "images")
        self.file_dir = os.path.join(self.upload_dir, "files")
        
        os.makedirs(self.video_dir, exist_ok=True)
        os.makedirs(self.image_dir, exist_ok=True)
        os.makedirs(self.file_dir, exist_ok=True)
        
        # Usage tracking
        self.usage_file = "upload_usage.json"
        self.usage = self._load_usage()
        
        logger.info(f"Initialized ContentUploader with config: {self.config}")
    
    def _load_usage(self) -> Dict:
        """Load usage data from file or create new if not exists"""
        import json
        
        if os.path.exists(self.usage_file):
            try:
                with open(self.usage_file, "r") as f:
                    usage = json.load(f)
                
                # Reset usage if it's a new day
                today = datetime.now().strftime("%Y-%m-%d")
                if usage.get("date") != today:
                    usage = self._create_new_usage()
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
            "uploaded": 0,
            "file_count": 0
        }
    
    def _save_usage(self):
        """Save usage data to file"""
        import json
        
        try:
            with open(self.usage_file, "w") as f:
                json.dump(self.usage, f)
        except Exception as e:
            logger.error(f"Error saving usage data: {e}")
    
    def _update_upload_usage(self, size_mb: float):
        """Update upload usage tracking"""
        self.usage["uploaded"] += size_mb
        self.usage["file_count"] += 1
        self._save_usage()
    
    def _check_upload_limit(self, size_mb: float) -> bool:
        """Check if upload would exceed daily limit"""
        if self.daily_upload_limit is None:
            return True
        
        return (self.usage["uploaded"] + size_mb) <= self.daily_upload_limit
    
    def _get_target_directory(self, file_type: str) -> str:
        """
        Get target directory based on file type
        
        Args:
            file_type: Type of file (video, image, file)
            
        Returns:
            Path to target directory
        """
        if file_type.lower() == "video":
            return self.video_dir
        elif file_type.lower() == "image":
            return self.image_dir
        else:
            return self.file_dir
    
    def upload_file(self, source_path: str, file_type: str, size_mb: float) -> Tuple[bool, str]:
        """
        Upload file to local project
        
        Args:
            source_path: Path to source file
            file_type: Type of file (video, image, file)
            size_mb: Size of file in MB
            
        Returns:
            Tuple of (success, message)
        """
        # Check if file exists
        if not os.path.exists(source_path):
            logger.error(f"Source file does not exist: {source_path}")
            return False, f"Source file does not exist: {source_path}"
        
        # Check if upload would exceed daily limit
        if not self._check_upload_limit(size_mb):
            logger.warning(f"Upload of {source_path} ({size_mb} MB) would exceed daily limit of {self.daily_upload_limit} MB")
            return False, f"Upload would exceed daily limit of {self.daily_upload_limit} MB"
        
        # Get target directory
        target_dir = self._get_target_directory(file_type)
        
        # Get filename
        filename = os.path.basename(source_path)
        
        # Create target path
        target_path = os.path.join(target_dir, filename)
        
        try:
            # Copy file to target directory
            shutil.copy2(source_path, target_path)
            
            # Update usage tracking
            self._update_upload_usage(size_mb)
            
            logger.info(f"Uploaded {source_path} to {target_path} ({size_mb} MB)")
            return True, f"Uploaded {filename} to {target_dir}"
            
        except Exception as e:
            logger.error(f"Error uploading {source_path} to {target_path}: {e}")
            return False, f"Error uploading {filename}: {str(e)}"
    
    def upload_multiple_files(self, files: List[Dict]) -> Tuple[int, int, List[str]]:
        """
        Upload multiple files to local project
        
        Args:
            files: List of dictionaries containing file information
                - path: Path to source file
                - type: Type of file (video, image, file)
                - size: Size of file in MB
            
        Returns:
            Tuple of (success_count, fail_count, error_messages)
        """
        success_count = 0
        fail_count = 0
        error_messages = []
        
        for file_info in files:
            source_path = file_info.get("path")
            file_type = file_info.get("type")
            size_mb = file_info.get("size")
            
            if not source_path or not file_type or not size_mb:
                fail_count += 1
                error_messages.append(f"Invalid file information: {file_info}")
                continue
            
            success, message = self.upload_file(source_path, file_type, size_mb)
            
            if success:
                success_count += 1
            else:
                fail_count += 1
                error_messages.append(message)
        
        return success_count, fail_count, error_messages
    
    def get_usage_stats(self) -> Dict:
        """
        Get current usage statistics
        
        Returns:
            Dictionary with usage statistics
        """
        return {
            "date": self.usage["date"],
            "uploaded": self.usage["uploaded"],
            "file_count": self.usage["file_count"],
            "upload_limit": self.daily_upload_limit,
            "upload_remaining": None if self.daily_upload_limit is None else max(0, self.daily_upload_limit - self.usage["uploaded"])
        }
    
    def update_config(self, new_config: Dict):
        """
        Update uploader configuration
        
        Args:
            new_config: New configuration parameters
        """
        self.config.update(new_config)
        
        # Update instance variables
        if "upload_dir" in new_config:
            self.upload_dir = new_config["upload_dir"]
            os.makedirs(self.upload_dir, exist_ok=True)
            
            # Update subdirectories
            self.video_dir = os.path.join(self.upload_dir, "videos")
            self.image_dir = os.path.join(self.upload_dir, "images")
            self.file_dir = os.path.join(self.upload_dir, "files")
            
            os.makedirs(self.video_dir, exist_ok=True)
            os.makedirs(self.image_dir, exist_ok=True)
            os.makedirs(self.file_dir, exist_ok=True)
            
        if "daily_upload_limit" in new_config:
            self.daily_upload_limit = new_config["daily_upload_limit"]
        
        logger.info(f"Updated configuration: {self.config}")

def main():
    """Test function to demonstrate uploader usage"""
    import sys
    
    # Example configuration
    config = {
        "upload_dir": "./uploads",
        "daily_upload_limit": 1000  # 1 GB daily limit
    }
    
    # Initialize uploader
    uploader = ContentUploader(config)
    
    # Check if file is provided
    if len(sys.argv) < 2:
        print("Usage: python uploader.py <file_path> [file_type]")
        return
    
    file_path = sys.argv[1]
    file_type = sys.argv[2] if len(sys.argv) > 2 else "file"
    
    # Get file size
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    
    # Upload file
    success, message = uploader.upload_file(file_path, file_type, size_mb)
    
    if success:
        print(f"Success: {message}")
    else:
        print(f"Error: {message}")
    
    # Get usage stats
    usage = uploader.get_usage_stats()
    print(f"Usage stats: {usage}")

if __name__ == "__main__":
    main()

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
import logging
import os
import json
from datetime import datetime

from scraper import BunkrScraper
from uploader import ContentUploader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("bunkr_api")

# Initialize FastAPI app
app = FastAPI(title="Bunkr Scraper API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Initialize scraper and uploader
scraper = BunkrScraper()
uploader = ContentUploader()

# Task storage
tasks = {}

# Models
class ContentItem(BaseModel):
    title: str
    url: str
    thumbnail: Optional[str] = None
    type: str
    size: float
    date: str

class ScraperConfig(BaseModel):
    min_size: Optional[float] = 0
    max_size: Optional[float] = None
    daily_download_limit: Optional[float] = None
    daily_upload_limit: Optional[float] = None
    download_dir: str = "./downloads"
    upload_dir: str = "./uploads"
    content_types: List[str] = ["videos", "images", "files"]
    time_period: str = "24h"

class DownloadRequest(BaseModel):
    items: List[ContentItem]

class UploadRequest(BaseModel):
    files: List[Dict[str, Any]]

class TaskStatus(BaseModel):
    id: str
    status: str
    progress: float
    completed: int = 0
    total: int = 0
    result: Optional[Dict[str, Any]] = None

# Routes
@app.get("/")
def read_root():
    return {"message": "Bunkr Scraper API", "version": "1.0.0"}

@app.get("/config")
def get_config():
    return scraper.config

@app.post("/config")
def update_config(config: ScraperConfig):
    scraper.update_config(config.dict())
    uploader.update_config({
        "upload_dir": config.upload_dir,
        "daily_upload_limit": config.daily_upload_limit
    })
    return scraper.config

@app.get("/scrape")
def scrape_content():
    videos = scraper.scrape_videos()
    images = scraper.scrape_images()
    files = scraper.scrape_files()
    return {
        "videos": videos,
        "images": images,
        "files": files
    }

@app.post("/download")
def download_content(request: DownloadRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    
    # Initialize task
    tasks[task_id] = {
        "id": task_id,
        "status": "pending",
        "progress": 0,
        "files": request.items,
        "completed": 0,
        "total": len(request.items)
    }
    
    # Start download in background
    background_tasks.add_task(
        download_task, 
        task_id=task_id, 
        items=request.items
    )
    
    return {"id": task_id, "status": "pending"}

def download_task(task_id: str, items: List[ContentItem]):
    try:
        tasks[task_id]["status"] = "running"
        
        total = len(items)
        completed = 0
        
        for i, item in enumerate(items):
            try:
                # Update progress
                tasks[task_id]["progress"] = i / total
                
                # Download file
                success = scraper.download_file(
                    url=item.url,
                    filename=item.title,
                    file_type=item.type,
                    file_size=item.size
                )
                
                if success:
                    completed += 1
                    tasks[task_id]["completed"] = completed
            except Exception as e:
                logger.error(f"Error downloading {item.url}: {str(e)}")
        
        # Update task status
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["progress"] = 1.0
        tasks[task_id]["result"] = {
            "success": True,
            "success_count": completed,
            "failed_count": total - completed,
            "message": f"Downloaded {completed} of {total} files"
        }
        
    except Exception as e:
        logger.error(f"Task {task_id} failed: {str(e)}")
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["result"] = {
            "success": False,
            "message": str(e)
        }

@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return tasks[task_id]

@app.post("/upload")
def upload_content(request: UploadRequest):
    try:
        result = uploader.upload_files(request.files)
        return result
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/usage")
def get_usage_stats():
    # Get current date
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Get download stats
    download_stats = scraper.get_download_stats()
    
    # Get upload stats
    upload_stats = uploader.get_upload_stats()
    
    # Calculate remaining limits
    download_remaining = None
    if scraper.config["daily_download_limit"]:
        download_remaining = scraper.config["daily_download_limit"] - download_stats["downloaded"]
        if download_remaining < 0:
            download_remaining = 0
    
    upload_remaining = None
    if uploader.config["daily_upload_limit"]:
        upload_remaining = uploader.config["daily_upload_limit"] - upload_stats["uploaded"]
        if upload_remaining < 0:
            upload_remaining = 0
    
    return {
        "date": today,
        "downloaded": download_stats["downloaded"],
        "uploaded": upload_stats["uploaded"],
        "download_limit": scraper.config["daily_download_limit"],
        "upload_limit": uploader.config["daily_upload_limit"],
        "download_remaining": download_remaining,
        "upload_remaining": upload_remaining,
        "file_count": upload_stats["file_count"]
    }

@app.get("/downloads")
def list_downloads():
    try:
        downloads = scraper.list_downloads()
        return {"files": downloads}
    except Exception as e:
        logger.error(f"Failed to list downloads: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/uploads")
def list_uploads():
    try:
        uploads = uploader.list_uploads()
        return {"files": uploads}
    except Exception as e:
        logger.error(f"Failed to list uploads: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

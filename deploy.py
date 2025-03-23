#!/usr/bin/env python3
"""
Bunkr Scraper - Deployment Script

This script prepares the application for deployment and provides access to the user.
"""

import os
import shutil
import subprocess
import sys

def create_readme():
    """Create README.md file with usage instructions"""
    readme_content = """# Bunkr Scraper Application

A web application for scraping content from bunkr.cr with customizable parameters.

## Features

- Scrape videos, images, and files from bunkr.cr
- Filter content by time period (24h, 7d, 30d, all)
- Filter content by file size (min/max size)
- Download content with progress tracking
- Upload downloaded content to your local project
- Set daily usage limits for downloads and uploads
- Monitor usage statistics

## Installation

### Prerequisites

- Python 3.10 or higher
- Node.js 14 or higher
- npm or yarn

### Setup

1. Clone this repository:
   ```
   git clone <repository-url>
   cd bunkr-scraper
   ```

2. Install backend dependencies:
   ```
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   pip install -r requirements.txt
   cd ..
   ```

3. Install frontend dependencies:
   ```
   cd frontend
   npm install
   cd ..
   ```

## Usage

### Starting the Application

Run the start script to launch both the backend and frontend:

```
python start.py
```

This will start:
- Backend API server at http://localhost:8000
- Frontend development server at http://localhost:3000

### Using the Application

1. **Configuration**: Set your scraping parameters
   - Select content types (videos, images, files)
   - Choose time period (24h, 7d, 30d, all)
   - Set size filters (min/max size in MB)
   - Configure daily usage limits

2. **Content Browser**: Browse and download content
   - View content matching your criteria
   - Select items to download
   - Monitor download progress

3. **Download Manager**: Manage downloaded files
   - View all downloaded files
   - Select files to upload to your local project
   - Organize content by type

4. **Usage Statistics**: Monitor your usage
   - Track daily download and upload usage
   - View remaining quota
   - Monitor file counts

## API Documentation

The backend provides a REST API at http://localhost:8000 with the following endpoints:

- `GET /config` - Get current configuration
- `POST /config` - Update configuration
- `GET /scrape` - Scrape content based on configuration
- `POST /download` - Download selected content
- `GET /tasks/{task_id}` - Check download task status
- `POST /upload` - Upload content to local project
- `GET /usage` - Get usage statistics
- `GET /downloads` - List downloaded files
- `GET /uploads` - List uploaded files

## Testing

Run the test script to verify the application functionality:

```
./test.sh
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
"""
    
    with open("README.md", "w") as f:
        f.write(readme_content)
    
    print("Created README.md with usage instructions")

def create_requirements():
    """Create requirements.txt file for backend"""
    requirements_content = """requests>=2.32.0
beautifulsoup4>=4.13.0
aiohttp>=3.11.0
tqdm>=4.67.0
fastapi>=0.115.0
uvicorn>=0.34.0
pydantic>=2.10.0
"""
    
    with open("backend/requirements.txt", "w") as f:
        f.write(requirements_content)
    
    print("Created requirements.txt for backend")

def create_deployment_package():
    """Create a deployment package (zip file) of the application"""
    # Create a dist directory if it doesn't exist
    os.makedirs("dist", exist_ok=True)
    
    # Create a zip file of the application
    shutil.make_archive("dist/bunkr-scraper", "zip", ".", 
                       include_dir_contents_only=False,
                       base_dir=".")
    
    print(f"Created deployment package at {os.path.abspath('dist/bunkr-scraper.zip')}")

def build_frontend():
    """Build the frontend for production"""
    os.chdir("frontend")
    
    # Run npm build
    try:
        subprocess.run(["npm", "run", "build"], check=True)
        print("Frontend built successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error building frontend: {e}")
        return False
    
    os.chdir("..")
    return True

def deploy_static_site():
    """Deploy the frontend as a static website"""
    # Check if frontend build directory exists
    if not os.path.exists("frontend/build"):
        print("Frontend build directory not found. Building frontend first...")
        if not build_frontend():
            return None
    
    # Deploy the static site
    try:
        from deploy_apply_deployment import deploy_apply_deployment
        result = deploy_apply_deployment(type="static", local_dir="frontend/build")
        return result
    except Exception as e:
        print(f"Error deploying static site: {e}")
        return None

def main():
    """Main function to deploy the application"""
    print("Preparing Bunkr Scraper Application for deployment...")
    
    # Create README.md
    create_readme()
    
    # Create requirements.txt
    create_requirements()
    
    # Build frontend
    print("Building frontend for production...")
    build_frontend()
    
    # Create deployment package
    create_deployment_package()
    
    # Deploy static site if requested
    deploy_option = input("Do you want to deploy the frontend as a static website? (y/n): ")
    if deploy_option.lower() == 'y':
        print("Deploying frontend as a static website...")
        result = deploy_static_site()
        if result:
            print(f"Frontend deployed successfully at: {result}")
            print("\nNote: The static site will need to connect to a running backend API server.")
            print("You can run the backend server using: cd backend && source venv/bin/activate && python -m uvicorn api:app --host 0.0.0.0 --port 8000")
    
    print("\nDeployment preparation completed!")
    print(f"Deployment package created at: {os.path.abspath('dist/bunkr-scraper.zip')}")
    print("\nTo use the application:")
    print("1. Extract the deployment package")
    print("2. Follow the instructions in README.md")
    print("3. Run 'python start.py' to start both backend and frontend servers")

if __name__ == "__main__":
    main()

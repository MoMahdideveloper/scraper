# Bunkr Scraper Application

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
   source venv/bin/activate  # On Windows: venv\Scripts\activate
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

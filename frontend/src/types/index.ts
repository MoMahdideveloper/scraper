export interface ContentItem {
  title: string;
  url: string;
  thumbnail?: string;
  type: string;
  size: number;
  date: string;
}

export interface ScraperConfig {
  min_size: number | null;
  max_size: number | null;
  daily_download_limit: number | null;
  daily_upload_limit: number | null;
  download_dir: string;
  upload_dir: string;
  content_types: string[];
  time_period: string;
}

export interface ScrapingResult {
  videos: ContentItem[];
  images: ContentItem[];
  files: ContentItem[];
}

export interface DownloadTask {
  id: string;
  status: string;
  progress: number;
  files: ContentItem[];
  completed: number;
  total: number;
  error?: string;
}

export interface UsageStats {
  date: string;
  downloaded: number;
  uploaded: number;
  download_limit: number | null;
  upload_limit: number | null;
  download_remaining: number | null;
  upload_remaining: number | null;
  file_count: number;
}

export interface UploadResult {
  success: boolean;
  uploaded: number;
  failed: number;
  message: string;
}

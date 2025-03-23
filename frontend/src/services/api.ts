import axios from 'axios';
import { 
  ScraperConfig, 
  ScrapingResult, 
  DownloadRequest, 
  UploadRequest, 
  DownloadResult, 
  UploadResult, 
  UsageStats, 
  TaskStatus,
  ContentItem
} from '../types';

const API_BASE_URL = 'http://localhost:8000';

// API service for interacting with the backend
export const apiService = {
  // Configuration endpoints
  getConfig: async (): Promise<ScraperConfig> => {
    const response = await axios.get(`${API_BASE_URL}/config`);
    return response.data;
  },

  updateConfig: async (config: Partial<ScraperConfig>): Promise<ScraperConfig> => {
    const response = await axios.post(`${API_BASE_URL}/config`, config);
    return response.data;
  },

  // Scraping endpoints
  scrapeContent: async (): Promise<ScrapingResult> => {
    const response = await axios.get(`${API_BASE_URL}/scrape`);
    return response.data;
  },

  // Download endpoints
  downloadContent: async (request: DownloadRequest): Promise<TaskStatus> => {
    const response = await axios.post(`${API_BASE_URL}/download`, request);
    return response.data;
  },

  getTaskStatus: async (taskId: string): Promise<TaskStatus> => {
    const response = await axios.get(`${API_BASE_URL}/tasks/${taskId}`);
    return response.data;
  },

  // Upload endpoints
  uploadContent: async (request: UploadRequest): Promise<UploadResult> => {
    const response = await axios.post(`${API_BASE_URL}/upload`, request);
    return response.data;
  },

  // Usage statistics
  getUsageStats: async (): Promise<UsageStats> => {
    const response = await axios.get(`${API_BASE_URL}/usage`);
    return response.data;
  },

  // List downloads and uploads
  listDownloads: async (): Promise<ContentItem[]> => {
    const response = await axios.get(`${API_BASE_URL}/downloads`);
    return response.data;
  },

  listUploads: async (): Promise<ContentItem[]> => {
    const response = await axios.get(`${API_BASE_URL}/uploads`);
    return response.data;
  }
};

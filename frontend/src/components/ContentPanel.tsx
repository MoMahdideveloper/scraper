import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Button,
  Grid,
  Divider,
  CircularProgress,
  Tabs,
  Tab,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Checkbox,
  IconButton,
  Alert,
  LinearProgress
} from '@mui/material';
import { 
  CloudDownload as DownloadIcon,
  CloudUpload as UploadIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { ScrapingResult, ContentItem } from '../types';
import { apiService } from '../services/api';

interface ContentPanelProps {
  config: any;
}

const ContentPanel: React.FC<ContentPanelProps> = ({ config }) => {
  const [activeTab, setActiveTab] = useState<string>('videos');
  const [scrapingResult, setScrapingResult] = useState<ScrapingResult>({ videos: [], images: [], files: [] });
  const [selectedItems, setSelectedItems] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [downloadTaskId, setDownloadTaskId] = useState<string | null>(null);
  const [downloadProgress, setDownloadProgress] = useState<number>(0);
  const [downloadStatus, setDownloadStatus] = useState<string>('');

  useEffect(() => {
    fetchContent();
  }, [config]);

  useEffect(() => {
    // Poll task status if there's an active download task
    let interval: NodeJS.Timeout;
    if (downloadTaskId && downloadStatus !== 'completed' && downloadStatus !== 'failed') {
      interval = setInterval(checkDownloadStatus, 2000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [downloadTaskId, downloadStatus]);

  const fetchContent = async () => {
    try {
      setLoading(true);
      const data = await apiService.scrapeContent();
      setScrapingResult(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch content');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: string) => {
    setActiveTab(newValue);
    setSelectedItems([]);
  };

  const handleItemSelect = (item: ContentItem) => {
    const isSelected = selectedItems.some(selected => selected.url === item.url);
    
    if (isSelected) {
      setSelectedItems(selectedItems.filter(selected => selected.url !== item.url));
    } else {
      setSelectedItems([...selectedItems, item]);
    }
  };

  const handleSelectAll = () => {
    if (selectedItems.length === getCurrentTabItems().length) {
      // Deselect all
      setSelectedItems([]);
    } else {
      // Select all
      setSelectedItems(getCurrentTabItems());
    }
  };

  const getCurrentTabItems = (): ContentItem[] => {
    switch (activeTab) {
      case 'videos':
        return scrapingResult.videos || [];
      case 'images':
        return scrapingResult.images || [];
      case 'files':
        return scrapingResult.files || [];
      default:
        return [];
    }
  };

  const startDownload = async () => {
    if (selectedItems.length === 0) return;
    
    try {
      setDownloadStatus('starting');
      setDownloadProgress(0);
      
      const response = await apiService.downloadContent({
        items: selectedItems
      });
      
      setDownloadTaskId(response.id);
      setDownloadStatus(response.status);
      setError(null);
      
      // Check status immediately
      checkDownloadStatus();
    } catch (err) {
      setError('Failed to start download');
      setDownloadStatus('failed');
      console.error(err);
    }
  };

  const checkDownloadStatus = async () => {
    if (!downloadTaskId) return;
    
    try {
      const status = await apiService.getTaskStatus(downloadTaskId);
      setDownloadStatus(status.status);
      setDownloadProgress(status.progress * 100);
      
      if (status.status === 'completed' || status.status === 'failed') {
        // Task finished
        if (status.result) {
          if (status.status === 'completed') {
            // Success
            console.log(`Downloaded ${status.result.success_count} files successfully`);
          } else {
            // Failed
            setError(`Download failed: ${status.result.message}`);
          }
        }
      }
    } catch (err) {
      console.error('Error checking download status:', err);
    }
  };

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5">
            Content Browser
          </Typography>
          <Button 
            startIcon={<RefreshIcon />} 
            onClick={fetchContent}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>
        
        <Divider sx={{ mb: 2 }} />
        
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            <Tabs
              value={activeTab}
              onChange={handleTabChange}
              indicatorColor="primary"
              textColor="primary"
              variant="fullWidth"
              sx={{ mb: 2 }}
            >
              <Tab 
                label={`Videos (${scrapingResult.videos?.length || 0})`} 
                value="videos" 
                disabled={!config.content_types.includes('videos')}
              />
              <Tab 
                label={`Images (${scrapingResult.images?.length || 0})`} 
                value="images"
                disabled={!config.content_types.includes('images')}
              />
              <Tab 
                label={`Files (${scrapingResult.files?.length || 0})`} 
                value="files"
                disabled={!config.content_types.includes('files')}
              />
            </Tabs>
            
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}
            
            {downloadStatus && downloadStatus !== 'completed' && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  Download Status: {downloadStatus.charAt(0).toUpperCase() + downloadStatus.slice(1)}
                </Typography>
                <LinearProgress 
                  variant={downloadStatus === 'pending' ? 'indeterminate' : 'determinate'} 
                  value={downloadProgress} 
                />
              </Box>
            )}
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Button 
                variant="outlined" 
                onClick={handleSelectAll}
                disabled={getCurrentTabItems().length === 0}
              >
                {selectedItems.length === getCurrentTabItems().length ? 'Deselect All' : 'Select All'}
              </Button>
              
              <Button 
                variant="contained" 
                color="primary" 
                startIcon={<DownloadIcon />}
                onClick={startDownload}
                disabled={selectedItems.length === 0 || downloadStatus === 'running' || downloadStatus === 'pending'}
              >
                Download Selected ({selectedItems.length})
              </Button>
            </Box>
            
            <List>
              {getCurrentTabItems().length === 0 ? (
                <Typography variant="body1" sx={{ p: 2, textAlign: 'center' }}>
                  No {activeTab} found matching your criteria
                </Typography>
              ) : (
                getCurrentTabItems().map((item, index) => (
                  <ListItem 
                    key={index} 
                    divider={index < getCurrentTabItems().length - 1}
                    secondaryAction={
                      <Checkbox
                        edge="end"
                        checked={selectedItems.some(selected => selected.url === item.url)}
                        onChange={() => handleItemSelect(item)}
                      />
                    }
                  >
                    <ListItemText
                      primary={item.title}
                      secondary={
                        <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                          <Chip 
                            label={`${item.size} MB`} 
                            size="small" 
                            color="primary" 
                            variant="outlined" 
                            sx={{ mr: 1 }}
                          />
                          <Typography variant="body2" color="text.secondary">
                            {item.type}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                ))
              )}
            </List>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default ContentPanel;

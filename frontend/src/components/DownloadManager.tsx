import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Grid,
  Divider,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Checkbox,
  Button,
  Chip,
  Alert
} from '@mui/material';
import { 
  CloudUpload as UploadIcon
} from '@mui/icons-material';
import { ContentItem } from '../types';
import { apiService } from '../services/api';

const DownloadManager: React.FC = () => {
  const [downloads, setDownloads] = useState<ContentItem[]>([]);
  const [selectedItems, setSelectedItems] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [uploading, setUploading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadResult, setUploadResult] = useState<any>(null);

  useEffect(() => {
    fetchDownloads();
  }, []);

  const fetchDownloads = async () => {
    try {
      setLoading(true);
      const data = await apiService.listDownloads();
      setDownloads(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch downloads');
      console.error(err);
    } finally {
      setLoading(false);
    }
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
    if (selectedItems.length === downloads.length) {
      // Deselect all
      setSelectedItems([]);
    } else {
      // Select all
      setSelectedItems(downloads);
    }
  };

  const handleUpload = async () => {
    if (selectedItems.length === 0) return;
    
    try {
      setUploading(true);
      setError(null);
      
      const files = selectedItems.map(item => ({
        path: item.url,
        type: item.type,
        size: item.size
      }));
      
      const result = await apiService.uploadContent({ files });
      setUploadResult(result);
      
      // Refresh downloads
      fetchDownloads();
    } catch (err) {
      setError('Failed to upload files');
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5">
            Download Manager
          </Typography>
          <Button 
            onClick={fetchDownloads}
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
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}
            
            {uploadResult && (
              <Alert 
                severity={uploadResult.fail_count > 0 ? "warning" : "success"} 
                sx={{ mb: 2 }}
                onClose={() => setUploadResult(null)}
              >
                {uploadResult.message}
                {uploadResult.fail_count > 0 && uploadResult.errors && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="body2">Errors:</Typography>
                    <ul>
                      {uploadResult.errors.map((err: string, index: number) => (
                        <li key={index}>{err}</li>
                      ))}
                    </ul>
                  </Box>
                )}
              </Alert>
            )}
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Button 
                variant="outlined" 
                onClick={handleSelectAll}
                disabled={downloads.length === 0}
              >
                {selectedItems.length === downloads.length ? 'Deselect All' : 'Select All'}
              </Button>
              
              <Button 
                variant="contained" 
                color="primary" 
                startIcon={<UploadIcon />}
                onClick={handleUpload}
                disabled={selectedItems.length === 0 || uploading}
              >
                {uploading ? 'Uploading...' : `Upload Selected (${selectedItems.length})`}
              </Button>
            </Box>
            
            <List>
              {downloads.length === 0 ? (
                <Typography variant="body1" sx={{ p: 2, textAlign: 'center' }}>
                  No downloaded files found
                </Typography>
              ) : (
                downloads.map((item, index) => (
                  <ListItem 
                    key={index} 
                    divider={index < downloads.length - 1}
                    secondaryAction={
                      <Checkbox
                        edge="end"
                        checked={selectedItems.some(selected => selected.path === item.path)}
                        onChange={() => handleItemSelect(item)}
                      />
                    }
                  >
                    <ListItemText
                      primary={item.name}
                      secondary={
                        <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                          <Chip 
                            label={item.size_text} 
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

export default DownloadManager;

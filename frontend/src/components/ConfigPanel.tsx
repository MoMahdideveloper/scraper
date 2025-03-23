import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  TextField, 
  Slider, 
  FormControl, 
  FormGroup, 
  FormControlLabel, 
  Checkbox, 
  Select, 
  MenuItem, 
  InputLabel, 
  Button,
  Grid,
  Divider
} from '@mui/material';
import { ScraperConfig } from '../types';
import { apiService } from '../services/api';

interface ConfigPanelProps {
  onConfigUpdate: () => void;
}

const ConfigPanel: React.FC<ConfigPanelProps> = ({ onConfigUpdate }) => {
  const [config, setConfig] = useState<ScraperConfig>({
    min_size: 0,
    max_size: null,
    daily_download_limit: null,
    daily_upload_limit: null,
    download_dir: './downloads',
    upload_dir: './uploads',
    content_types: ['videos', 'images', 'files'],
    time_period: '24h'
  });

  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      setLoading(true);
      const data = await apiService.getConfig();
      setConfig(data);
      setError(null);
    } catch (err) {
      setError('Failed to load configuration');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleContentTypeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = event.target;
    
    if (checked) {
      setConfig({
        ...config,
        content_types: [...config.content_types, name]
      });
    } else {
      setConfig({
        ...config,
        content_types: config.content_types.filter(type => type !== name)
      });
    }
  };

  const handleTimePeriodChange = (event: any) => {
    setConfig({
      ...config,
      time_period: event.target.value
    });
  };

  const handleMinSizeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseFloat(event.target.value);
    setConfig({
      ...config,
      min_size: isNaN(value) ? 0 : value
    });
  };

  const handleMaxSizeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value === '' ? null : parseFloat(event.target.value);
    setConfig({
      ...config,
      max_size: isNaN(value as number) ? null : value
    });
  };

  const handleDownloadLimitChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value === '' ? null : parseFloat(event.target.value);
    setConfig({
      ...config,
      daily_download_limit: isNaN(value as number) ? null : value
    });
  };

  const handleUploadLimitChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value === '' ? null : parseFloat(event.target.value);
    setConfig({
      ...config,
      daily_upload_limit: isNaN(value as number) ? null : value
    });
  };

  const handleSaveConfig = async () => {
    try {
      setLoading(true);
      await apiService.updateConfig(config);
      setError(null);
      onConfigUpdate();
    } catch (err) {
      setError('Failed to save configuration');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          Scraper Configuration
        </Typography>
        
        <Divider sx={{ my: 2 }} />
        
        <Grid container spacing={3}>
          {/* Content Types */}
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle1" gutterBottom>
              Content Types
            </Typography>
            <FormControl component="fieldset">
              <FormGroup>
                <FormControlLabel
                  control={
                    <Checkbox 
                      checked={config.content_types.includes('videos')} 
                      onChange={handleContentTypeChange} 
                      name="videos" 
                    />
                  }
                  label="Videos"
                />
                <FormControlLabel
                  control={
                    <Checkbox 
                      checked={config.content_types.includes('images')} 
                      onChange={handleContentTypeChange} 
                      name="images" 
                    />
                  }
                  label="Images"
                />
                <FormControlLabel
                  control={
                    <Checkbox 
                      checked={config.content_types.includes('files')} 
                      onChange={handleContentTypeChange} 
                      name="files" 
                    />
                  }
                  label="Files"
                />
              </FormGroup>
            </FormControl>
          </Grid>
          
          {/* Time Period */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel id="time-period-label">Time Period</InputLabel>
              <Select
                labelId="time-period-label"
                value={config.time_period}
                label="Time Period"
                onChange={handleTimePeriodChange}
              >
                <MenuItem value="24h">Last 24 Hours</MenuItem>
                <MenuItem value="7d">Last 7 Days</MenuItem>
                <MenuItem value="30d">Last 30 Days</MenuItem>
                <MenuItem value="all">All Time</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          {/* Size Filters */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" gutterBottom>
              Size Filters (MB)
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Minimum Size (MB)"
                  type="number"
                  fullWidth
                  value={config.min_size}
                  onChange={handleMinSizeChange}
                  InputProps={{ inputProps: { min: 0 } }}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Maximum Size (MB, empty for no limit)"
                  type="number"
                  fullWidth
                  value={config.max_size === null ? '' : config.max_size}
                  onChange={handleMaxSizeChange}
                  InputProps={{ inputProps: { min: 0 } }}
                />
              </Grid>
            </Grid>
          </Grid>
          
          {/* Usage Limits */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" gutterBottom>
              Daily Usage Limits (MB)
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Daily Download Limit (MB, empty for no limit)"
                  type="number"
                  fullWidth
                  value={config.daily_download_limit === null ? '' : config.daily_download_limit}
                  onChange={handleDownloadLimitChange}
                  InputProps={{ inputProps: { min: 0 } }}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Daily Upload Limit (MB, empty for no limit)"
                  type="number"
                  fullWidth
                  value={config.daily_upload_limit === null ? '' : config.daily_upload_limit}
                  onChange={handleUploadLimitChange}
                  InputProps={{ inputProps: { min: 0 } }}
                />
              </Grid>
            </Grid>
          </Grid>
        </Grid>
        
        {error && (
          <Typography color="error" sx={{ mt: 2 }}>
            {error}
          </Typography>
        )}
        
        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
          <Button 
            variant="contained" 
            color="primary" 
            onClick={handleSaveConfig}
            disabled={loading}
          >
            {loading ? 'Saving...' : 'Save Configuration'}
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

export default ConfigPanel;

import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Grid,
  Divider,
  CircularProgress,
  LinearProgress,
  Paper
} from '@mui/material';
import { UsageStats } from '../types';
import { apiService } from '../services/api';

const UsagePanel: React.FC = () => {
  const [usageStats, setUsageStats] = useState<UsageStats | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchUsageStats();
    // Set up polling every 30 seconds
    const interval = setInterval(fetchUsageStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchUsageStats = async () => {
    try {
      setLoading(true);
      const data = await apiService.getUsageStats();
      setUsageStats(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch usage statistics');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const calculatePercentage = (used: number, limit: number | null): number => {
    if (!limit) return 0;
    return Math.min(100, (used / limit) * 100);
  };

  if (loading && !usageStats) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          Usage Statistics
        </Typography>
        
        <Divider sx={{ my: 2 }} />
        
        {usageStats ? (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Paper elevation={2} sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Download Usage
                </Typography>
                <Typography variant="h6">
                  {usageStats.downloaded.toFixed(2)} MB
                  {usageStats.download_limit && ` / ${usageStats.download_limit} MB`}
                </Typography>
                {usageStats.download_limit && (
                  <Box sx={{ mt: 1 }}>
                    <LinearProgress 
                      variant="determinate" 
                      value={calculatePercentage(usageStats.downloaded, usageStats.download_limit)} 
                      color={usageStats.downloaded > (usageStats.download_limit * 0.8) ? "error" : "primary"}
                    />
                    <Typography variant="body2" sx={{ mt: 0.5 }}>
                      {usageStats.download_remaining !== null 
                        ? `${usageStats.download_remaining.toFixed(2)} MB remaining today` 
                        : 'No limit set'}
                    </Typography>
                  </Box>
                )}
              </Paper>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Paper elevation={2} sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Upload Usage
                </Typography>
                <Typography variant="h6">
                  {usageStats.uploaded.toFixed(2)} MB
                  {usageStats.upload_limit && ` / ${usageStats.upload_limit} MB`}
                </Typography>
                {usageStats.upload_limit && (
                  <Box sx={{ mt: 1 }}>
                    <LinearProgress 
                      variant="determinate" 
                      value={calculatePercentage(usageStats.uploaded, usageStats.upload_limit)} 
                      color={usageStats.uploaded > (usageStats.upload_limit * 0.8) ? "error" : "primary"}
                    />
                    <Typography variant="body2" sx={{ mt: 0.5 }}>
                      {usageStats.upload_remaining !== null 
                        ? `${usageStats.upload_remaining.toFixed(2)} MB remaining today` 
                        : 'No limit set'}
                    </Typography>
                  </Box>
                )}
              </Paper>
            </Grid>
            
            <Grid item xs={12}>
              <Paper elevation={2} sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Summary
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2">Date: {usageStats.date}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">Files Uploaded: {usageStats.file_count}</Typography>
                  </Grid>
                </Grid>
              </Paper>
            </Grid>
          </Grid>
        ) : (
          <Typography variant="body1" color="error">
            {error || 'No usage data available'}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

export default UsagePanel;

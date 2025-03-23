import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Box, 
  Grid, 
  CssBaseline, 
  AppBar, 
  Toolbar, 
  Typography, 
  Tabs, 
  Tab,
  Paper
} from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import ConfigPanel from './components/ConfigPanel';
import ContentPanel from './components/ContentPanel';
import DownloadManager from './components/DownloadManager';
import UsagePanel from './components/UsagePanel';
import { ScraperConfig } from './types';
import { apiService } from './services/api';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
});

function App() {
  const [activeTab, setActiveTab] = useState<number>(0);
  const [config, setConfig] = useState<ScraperConfig | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      setLoading(true);
      const data = await apiService.getConfig();
      setConfig(data);
    } catch (error) {
      console.error('Failed to fetch configuration:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleConfigUpdate = () => {
    fetchConfig();
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Bunkr Scraper
            </Typography>
          </Toolbar>
        </AppBar>
        
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            indicatorColor="primary"
            textColor="primary"
            variant="fullWidth"
            sx={{ mb: 3 }}
          >
            <Tab label="Content Browser" />
            <Tab label="Download Manager" />
            <Tab label="Configuration" />
            <Tab label="Usage Statistics" />
          </Tabs>
          
          {loading ? (
            <Paper sx={{ p: 3, textAlign: 'center' }}>
              <Typography>Loading application...</Typography>
            </Paper>
          ) : (
            <>
              {activeTab === 0 && config && (
                <ContentPanel config={config} />
              )}
              
              {activeTab === 1 && (
                <DownloadManager />
              )}
              
              {activeTab === 2 && (
                <ConfigPanel onConfigUpdate={handleConfigUpdate} />
              )}
              
              {activeTab === 3 && (
                <UsagePanel />
              )}
            </>
          )}
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;

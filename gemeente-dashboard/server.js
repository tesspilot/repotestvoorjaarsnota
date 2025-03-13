const express = require('express');
const path = require('path');
const fs = require('fs');
const { scrapeData, processData } = require('./scraper');

// Initialize express app
const app = express();
const PORT = process.env.PORT || 3000;

// Set the view engine to ejs
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Static files
app.use(express.static(path.join(__dirname, 'public')));

// Data directory
const dataDir = path.join(__dirname, 'data');
const dataFilePath = path.join(dataDir, 'scraped-data.json');

// Create data directory if it doesn't exist
if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
}

// Main dashboard route
app.get('/', async (req, res) => {
    try {
        let scrapedData;
        let processedData;
        let dataExists = fs.existsSync(dataFilePath);
        let needsRefresh = false;
        
        // Check if data exists and how old it is
        if (dataExists) {
            const fileData = fs.readFileSync(dataFilePath, 'utf8');
            scrapedData = JSON.parse(fileData);
            
            // Check if data is older than 1 day
            const lastUpdated = new Date(scrapedData.lastUpdated);
            const oneDayAgo = new Date();
            oneDayAgo.setDate(oneDayAgo.getDate() - 1);
            
            if (lastUpdated < oneDayAgo) {
                needsRefresh = true;
            }
        }
        
        // If no data or needs refresh, scrape fresh data
        if (!dataExists || needsRefresh) {
            scrapedData = await scrapeData();
        }
        
        // Process the data for dashboard metrics
        processedData = processData(scrapedData);
        
        // Render the dashboard with the data
        res.render('dashboard', {
            title: 'Gemeente Rotterdam Voorjaarsnota 2024 Dashboard',
            rawData: scrapedData,
            metrics: processedData
        });
    } catch (error) {
        console.error('Error loading dashboard:', error);
        res.status(500).render('error', { 
            message: 'Er is een fout opgetreden bij het laden van het dashboard.',
            error: error.toString()
        });
    }
});

// API endpoint to get the raw data
app.get('/api/data', (req, res) => {
    try {
        if (fs.existsSync(dataFilePath)) {
            const fileData = fs.readFileSync(dataFilePath, 'utf8');
            res.json(JSON.parse(fileData));
        } else {
            res.status(404).json({ error: 'No data available' });
        }
    } catch (error) {
        res.status(500).json({ error: error.toString() });
    }
});

// API endpoint to get the processed metrics
app.get('/api/metrics', (req, res) => {
    try {
        if (fs.existsSync(dataFilePath)) {
            const fileData = fs.readFileSync(dataFilePath, 'utf8');
            const scrapedData = JSON.parse(fileData);
            const processedData = processData(scrapedData);
            res.json(processedData);
        } else {
            res.status(404).json({ error: 'No data available' });
        }
    } catch (error) {
        res.status(500).json({ error: error.toString() });
    }
});

// Refresh data endpoint
app.get('/refresh', async (req, res) => {
    try {
        const scrapedData = await scrapeData();
        const processedData = processData(scrapedData);
        
        res.json({
            success: true,
            message: 'Data successfully refreshed',
            lastUpdated: scrapedData.lastUpdated
        });
    } catch (error) {
        console.error('Error refreshing data:', error);
        res.status(500).json({ 
            success: false,
            error: error.toString()
        });
    }
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
    console.log(`Dashboard available at http://localhost:${PORT}`);
});

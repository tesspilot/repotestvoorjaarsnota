const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

// URL to scrape
const URL = 'https://abx10.archiefweb.eu:8443/watdoetdegemeentevoorjaarsnota2024/20241114091054mp_/https://archieven.watdoetdegemeente.rotterdam.nl/voorjaarsnota2024/hoofdlijnen/01-voortgang/';

// Function to scrape the data
async function scrapeData() {
    console.log('Starting browser...');
    
    // Launch the browser with specific settings to bypass some restrictions
    const browser = await puppeteer.launch({
        headless: 'new',
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process'
        ]
    });

    try {
        console.log('Opening new page...');
        const page = await browser.newPage();
        
        // Set viewport size
        await page.setViewport({ width: 1280, height: 800 });
        
        // Set user agent to avoid detection as a bot
        await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36');
        
        // Navigate to URL
        console.log(`Navigating to ${URL}...`);
        await page.goto(URL, { waitUntil: 'networkidle2', timeout: 60000 });
        
        // Wait for content to load
        await page.waitForSelector('body', { timeout: 60000 });
        
        console.log('Page loaded, extracting data...');

        // Extract all text content for processing
        const pageData = await page.evaluate(() => {
            // Extract page title
            const pageTitle = document.title;
            
            // Extract main content sections
            const sections = Array.from(document.querySelectorAll('section, div.section, div.content-block, article'))
                .map(section => {
                    // Get headings
                    const headings = Array.from(section.querySelectorAll('h1, h2, h3, h4, h5'))
                        .map(h => h.innerText.trim());
                    
                    // Get paragraphs
                    const paragraphs = Array.from(section.querySelectorAll('p'))
                        .map(p => p.innerText.trim())
                        .filter(text => text.length > 0);
                    
                    // Get list items
                    const listItems = Array.from(section.querySelectorAll('li'))
                        .map(li => li.innerText.trim())
                        .filter(text => text.length > 0);
                    
                    // Get tables
                    const tables = Array.from(section.querySelectorAll('table'))
                        .map(table => {
                            const headers = Array.from(table.querySelectorAll('th'))
                                .map(th => th.innerText.trim());
                            
                            const rows = Array.from(table.querySelectorAll('tr'))
                                .map(tr => Array.from(tr.querySelectorAll('td'))
                                    .map(td => td.innerText.trim()));
                            
                            return { headers, rows };
                        });
                    
                    // Get any data figures
                    const figures = Array.from(section.querySelectorAll('.figure, figure, .data-visualization'))
                        .map(fig => {
                            const caption = fig.querySelector('figcaption, .caption')?.innerText.trim() || '';
                            const dataText = fig.innerText.trim();
                            return { caption, dataText };
                        });
                    
                    // Extract any numeric data (percentages, amounts, etc.)
                    const numericData = section.innerText.match(/\d+[.,]?\d*\s?(%|miljoen|duizend|euro|€)/g) || [];
                    
                    return {
                        headings,
                        paragraphs,
                        listItems,
                        tables,
                        figures,
                        numericData
                    };
                })
                .filter(section => 
                    section.headings.length > 0 || 
                    section.paragraphs.length > 0 || 
                    section.listItems.length > 0 ||
                    section.tables.length > 0 ||
                    section.figures.length > 0
                );
            
            // Extract any charts or graphs data
            const chartData = Array.from(document.querySelectorAll('[data-chart], .chart, .graph'))
                .map(chart => {
                    // Attempt to extract data attributes
                    const dataAttributes = {};
                    Array.from(chart.attributes)
                        .filter(attr => attr.name.startsWith('data-'))
                        .forEach(attr => {
                            dataAttributes[attr.name] = attr.value;
                        });
                    
                    return {
                        id: chart.id || '',
                        className: chart.className || '',
                        dataAttributes,
                        innerText: chart.innerText.trim()
                    };
                });
            
            // Try to extract meta information
            const metaInfo = {
                description: document.querySelector('meta[name="description"]')?.content || '',
                keywords: document.querySelector('meta[name="keywords"]')?.content || '',
                author: document.querySelector('meta[name="author"]')?.content || '',
                date: document.querySelector('meta[name="date"]')?.content || 
                      document.querySelector('.date, .published-date')?.innerText.trim() || ''
            };
            
            // Extract budget/financial data specifically
            const financialData = [];
            const financialElements = document.querySelectorAll('.financial, .budget, .finance, .amount, .money');
            financialElements.forEach(el => {
                const category = el.querySelector('.category, .title')?.innerText.trim() || '';
                const amount = el.querySelector('.amount, .value')?.innerText.trim() || '';
                const description = el.querySelector('.description')?.innerText.trim() || '';
                
                if (category || amount) {
                    financialData.push({ category, amount, description });
                }
            });
            
            // Get all numeric data that looks like financial information
            const allFinancialMatches = document.body.innerText.match(/€\s?\d+[.,]?\d*|\d+[.,]?\d*\s?(?:miljoen|duizend|euro|€)/g) || [];
            
            return {
                pageTitle,
                metaInfo,
                sections,
                chartData,
                financialData,
                allFinancialMatches
            };
        });
        
        console.log('Extracting screenshots of charts and tables...');
        
        // Take screenshots of charts, graphs, and tables
        const chartElements = await page.$$('.chart, [data-chart], .graph, .visualization, table');
        const screenshots = [];
        
        for (let i = 0; i < chartElements.length; i++) {
            try {
                const element = chartElements[i];
                const fileName = `chart_${i}.png`;
                const filePath = path.join(__dirname, 'public', 'images', fileName);
                
                // Ensure directory exists
                fs.mkdirSync(path.join(__dirname, 'public', 'images'), { recursive: true });
                
                // Take screenshot of the element
                await element.screenshot({ path: filePath });
                
                screenshots.push({
                    fileName,
                    index: i
                });
            } catch (err) {
                console.error(`Error taking screenshot for element ${i}:`, err);
            }
        }
        
        // Save the data
        const dataToSave = {
            ...pageData,
            screenshots,
            lastUpdated: new Date().toISOString()
        };
        
        // Ensure directory exists
        fs.mkdirSync(path.join(__dirname, 'data'), { recursive: true });
        
        // Write to file
        fs.writeFileSync(
            path.join(__dirname, 'data', 'scraped-data.json'),
            JSON.stringify(dataToSave, null, 2)
        );
        
        console.log('Data extraction complete!');
        return dataToSave;
    } catch (error) {
        console.error('Error during scraping:', error);
        throw error;
    } finally {
        await browser.close();
        console.log('Browser closed');
    }
}

// Process the data to extract key metrics and prepare for dashboard
function processData(data) {
    // Extract key metrics and indicators
    const metrics = {
        totalSections: data.sections.length,
        financialItems: data.financialData.length,
        lastUpdated: data.lastUpdated,
        keyCategories: [],
        budgetSummary: {
            total: 0,
            categories: {}
        }
    };
    
    // Process financial data
    if (data.financialData.length > 0) {
        data.financialData.forEach(item => {
            // Remove currency symbols and convert to number
            let amount = 0;
            if (item.amount) {
                // Extract number from formats like "€ 10,5 miljoen" or "15.000 euro"
                const numberMatch = item.amount.match(/\d+[.,]?\d*/);
                if (numberMatch) {
                    amount = parseFloat(numberMatch[0].replace(',', '.'));
                    
                    // Apply multiplier if needed
                    if (item.amount.includes('miljoen')) {
                        amount *= 1000000;
                    } else if (item.amount.includes('duizend')) {
                        amount *= 1000;
                    }
                }
            }
            
            if (item.category && amount) {
                // Add to categories
                if (!metrics.budgetSummary.categories[item.category]) {
                    metrics.budgetSummary.categories[item.category] = 0;
                }
                metrics.budgetSummary.categories[item.category] += amount;
                metrics.budgetSummary.total += amount;
                
                // Track key categories
                if (!metrics.keyCategories.includes(item.category)) {
                    metrics.keyCategories.push(item.category);
                }
            }
        });
    } else {
        // If no structured financial data was found, try to parse from text
        const allAmounts = data.allFinancialMatches || [];
        let tempTotal = 0;
        
        allAmounts.forEach((amountStr, index) => {
            // Extract number
            const numberMatch = amountStr.match(/\d+[.,]?\d*/);
            if (numberMatch) {
                let amount = parseFloat(numberMatch[0].replace(',', '.'));
                
                // Apply multiplier if needed
                if (amountStr.includes('miljoen')) {
                    amount *= 1000000;
                } else if (amountStr.includes('duizend')) {
                    amount *= 1000;
                }
                
                const category = `Category ${index + 1}`;
                if (!metrics.budgetSummary.categories[category]) {
                    metrics.budgetSummary.categories[category] = 0;
                }
                metrics.budgetSummary.categories[category] += amount;
                tempTotal += amount;
            }
        });
        
        metrics.budgetSummary.total = tempTotal;
    }
    
    // Extract main topics/themes
    const topics = new Set();
    data.sections.forEach(section => {
        section.headings.forEach(heading => {
            // Extract potential topics from headings
            const words = heading.split(/\s+/);
            words.forEach(word => {
                if (word.length > 4 && !['voor', 'naar', 'deze', 'door', 'over'].includes(word.toLowerCase())) {
                    topics.add(word);
                }
            });
        });
    });
    
    metrics.keyTopics = Array.from(topics).slice(0, 10); // Top 10 topics
    
    return metrics;
}

// Export functions for use in the server
module.exports = {
    scrapeData,
    processData
};

// If script is run directly, execute the scraping
if (require.main === module) {
    console.log('Running scraper directly...');
    scrapeData()
        .then(data => {
            const processed = processData(data);
            console.log('Processed data:', processed);
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

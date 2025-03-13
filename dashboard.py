import dash
from dash import dcc, html, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import re
import datetime
import requests
from bs4 import BeautifulSoup
import networkx as nx
import json
import os

# URL to scrape
URL = "https://abx10.archiefweb.eu:8443/watdoetdegemeentevoorjaarsnota2024/20241114091054mp_/https://archieven.watdoetdegemeente.rotterdam.nl/voorjaarsnota2024/hoofdlijnen/01-voortgang/"

# Function to scrape data from the website
def scrape_data():
    try:
        # Check if we have cached data and it's recent (less than 1 hour old)
        if os.path.exists('data/scraped_data.json'):
            with open('data/scraped_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Use the cached data
                print("Using cached data")
                return data
        
        # If no cached data or it's old, scrape new data
        # Send a request to the URL
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        }
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract page title
        page_title = soup.title.text if soup.title else "Voorjaarsnota 2024 Dashboard"
        
        # Extract headings
        headings = []
        for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            for heading in soup.find_all(tag):
                headings.append({
                    'level': int(tag[1]),
                    'text': heading.text.strip()
                })
        
        # Extract paragraphs
        paragraphs = [p.text.strip() for p in soup.find_all('p') if p.text.strip()]
        
        # Extract list items
        list_items = [li.text.strip() for li in soup.find_all('li') if li.text.strip()]
        
        # Extract tables
        tables = []
        for table in soup.find_all('table'):
            headers = [th.text.strip() for th in table.find_all('th')]
            rows = []
            for tr in table.find_all('tr'):
                row = [td.text.strip() for td in tr.find_all('td')]
                if row:
                    rows.append(row)
            tables.append({'headers': headers, 'rows': rows})
        
        # Extract numeric data (percentages, amounts, etc.)
        text = soup.get_text()
        numeric_data = re.findall(r'\d+[.,]?\d*\s?(%|miljoen|duizend|euro|€)', text)
        
        # Extract images
        images = []
        for img in soup.find_all('img'):
            images.append({
                'src': img.get('src', ''),
                'alt': img.get('alt', ''),
                'width': img.get('width', ''),
                'height': img.get('height', '')
            })
        
        # Create structured data
        data = {
            'page_title': page_title,
            'headings': headings,
            'paragraphs': paragraphs,
            'list_items': list_items,
            'tables': tables,
            'numeric_data': numeric_data,
            'images': images,
            'full_text': text,
            'last_updated': datetime.datetime.now().isoformat()
        }
        
        # Save data to file
        os.makedirs('data', exist_ok=True)
        with open('data/scraped_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        return data
    except Exception as e:
        print(f"Error scraping data: {e}")
        
        # If scraping fails, try to load from file
        if os.path.exists('data/scraped_data.json'):
            with open('data/scraped_data.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # If no file exists, return sample data
        return {
            'page_title': "Voorjaarsnota 2024 Dashboard",
            'headings': [
                {'level': 1, 'text': 'Voorjaarsnota 2024'},
                {'level': 2, 'text': 'Voortgang'},
                {'level': 2, 'text': 'Financiële Ontwikkelingen'},
                {'level': 2, 'text': 'Beleidsprioriteiten'},
                {'level': 3, 'text': 'Wonen'},
                {'level': 3, 'text': 'Mobiliteit'},
                {'level': 3, 'text': 'Duurzaamheid'},
                {'level': 3, 'text': 'Economie'},
                {'level': 3, 'text': 'Sociaal Domein'},
            ],
            'paragraphs': [
                "De Voorjaarsnota 2024 geeft inzicht in de voortgang van de uitvoering van het collegeprogramma en de financiële ontwikkelingen.",
                "Rotterdam investeert in 2024 fors in de stad met een focus op wonen, mobiliteit en duurzaamheid.",
                "De gemeente Rotterdam zet in op het bouwen van 3.000 nieuwe woningen in 2024.",
                "Voor het verbeteren van de mobiliteit is €45 miljoen beschikbaar gesteld.",
                "De duurzaamheidstransitie wordt versneld met een investering van €30 miljoen.",
                "De economische ontwikkeling wordt gestimuleerd met €20 miljoen voor innovatie en ondernemerschap.",
                "In het sociaal domein wordt €60 miljoen geïnvesteerd om armoede tegen te gaan en kansengelijkheid te bevorderen."
            ],
            'list_items': [
                "Bouw van 3.000 nieuwe woningen",
                "Verbetering van OV-verbindingen",
                "Verduurzaming van 5.000 woningen",
                "Ondersteuning van 500 startups en scale-ups",
                "Uitbreiding van armoedebestrijdingsprogramma's",
                "Vergroening van 10 wijken",
                "Aanleg van 15 km nieuwe fietspaden"
            ],
            'tables': [
                {
                    'headers': ['Programma', 'Budget 2024 (miljoen €)', 'Verschil t.o.v. 2023 (miljoen €)'],
                    'rows': [
                        ['Wonen', '150', '+25'],
                        ['Mobiliteit', '120', '+45'],
                        ['Duurzaamheid', '80', '+30'],
                        ['Economie', '70', '+20'],
                        ['Sociaal Domein', '200', '+60'],
                        ['Veiligheid', '90', '+15'],
                        ['Cultuur', '40', '+5']
                    ]
                },
                {
                    'headers': ['Wijk', 'Aantal nieuwe woningen', 'Investering (miljoen €)'],
                    'rows': [
                        ['Centrum', '800', '40'],
                        ['Noord', '600', '30'],
                        ['Zuid', '700', '35'],
                        ['West', '500', '25'],
                        ['Oost', '400', '20']
                    ]
                }
            ],
            'numeric_data': [
                '3.000 woningen', 
                '€45 miljoen', 
                '€30 miljoen', 
                '€20 miljoen', 
                '€60 miljoen',
                '5.000 woningen',
                '500 startups',
                '10 wijken',
                '15 km',
                '150 miljoen €',
                '120 miljoen €',
                '80 miljoen €',
                '70 miljoen €',
                '200 miljoen €',
                '90 miljoen €',
                '40 miljoen €',
                '800 woningen',
                '600 woningen',
                '700 woningen',
                '500 woningen',
                '400 woningen'
            ],
            'images': [],
            'full_text': "Voorjaarsnota 2024 Rotterdam - Voortgang en Financiële Ontwikkelingen",
            'last_updated': datetime.datetime.now().isoformat()
        }

# Function to process data for dashboard
def process_data(data):
    # Extract financial data
    financial_data = []
    
    # First try to extract from tables that look like financial tables
    for table in data['tables']:
        if table['headers'] and table['rows']:
            # Look for headers that might indicate financial data
            financial_headers = [h for h in table['headers'] if any(term in h.lower() for term in ['budget', 'bedrag', 'miljoen', 'euro', '€', 'kosten', 'investering'])]
            
            if financial_headers:
                # Find the index of the financial column
                financial_col_idx = table['headers'].index(financial_headers[0])
                category_col_idx = 0  # Assume first column is category
                
                # Extract financial data from this table
                for row in table['rows']:
                    if len(row) > financial_col_idx and len(row) > category_col_idx:
                        category = row[category_col_idx]
                        value_str = row[financial_col_idx]
                        
                        # Try to extract numeric value
                        try:
                            # Handle different formats (e.g., "€ 10 miljoen", "10,5 miljoen €")
                            value_str = value_str.replace('.', '').replace(',', '.')
                            
                            # Extract the numeric part
                            match = re.search(r'([-+]?\d+(?:\.\d+)?)', value_str)
                            if match:
                                value = float(match.group(1))
                                
                                # Apply multiplier based on units
                                if 'miljoen' in value_str.lower() or 'mln' in value_str.lower():
                                    value *= 1000000
                                elif 'duizend' in value_str.lower() or 'k' in value_str.lower():
                                    value *= 1000
                                
                                financial_data.append({
                                    'category': category,
                                    'amount': value,
                                    'original_text': row[financial_col_idx],
                                    'source': 'table'
                                })
                        except (ValueError, AttributeError):
                            pass
    
    # Also extract from paragraphs and list items
    all_text = data['paragraphs'] + data['list_items']
    for text in all_text:
        # Look for patterns like "€X miljoen voor Y" or "X miljoen euro voor Y"
        matches = re.finditer(r'(?:€\s*)?(\d+(?:[.,]\d+)?)\s*(miljoen|mln|duizend|k)?\s*(?:euro|€)?\s*(?:voor|aan|in|op)\s*([^,.]+)', text, re.IGNORECASE)
        for match in matches:
            try:
                value_str = match.group(1).replace(',', '.')
                value = float(value_str)
                
                # Apply multiplier
                if match.group(2):
                    if 'miljoen' in match.group(2).lower() or 'mln' in match.group(2).lower():
                        value *= 1000000
                    elif 'duizend' in match.group(2).lower() or 'k' in match.group(2).lower():
                        value *= 1000
                
                category = match.group(3).strip()
                
                financial_data.append({
                    'category': category,
                    'amount': value,
                    'original_text': match.group(0),
                    'source': 'text'
                })
            except (ValueError, AttributeError):
                pass
    
    # Also look for specific patterns in numeric_data
    for item in data['numeric_data']:
        match = re.match(r'(?:€\s*)?(\d+(?:[.,]\d+)?)\s*(miljoen|mln|duizend|k)?\s*(?:euro|€)?\s*', item, re.IGNORECASE)
        if match:
            try:
                value_str = match.group(1).replace(',', '.')
                value = float(value_str)
                
                # Apply multiplier
                if match.group(2):
                    if 'miljoen' in match.group(2).lower() or 'mln' in match.group(2).lower():
                        value *= 1000000
                    elif 'duizend' in match.group(2).lower() or 'k' in match.group(2).lower():
                        value *= 1000
                
                # Try to find a category from context
                category = "Overig"  # Default
                
                financial_data.append({
                    'category': category,
                    'amount': value,
                    'original_text': item,
                    'source': 'numeric_data'
                })
            except (ValueError, AttributeError):
                pass
    
    # Extract topics (words that appear frequently)
    text = data['full_text'].lower()
    
    # List of common Dutch stopwords to filter out
    stopwords = ['de', 'het', 'een', 'en', 'van', 'in', 'op', 'voor', 'met', 'door', 'aan', 'is', 'zijn', 'worden', 'werd']
    
    # Extract words and filter
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text)
    words = [word for word in words if word not in stopwords]
    
    # Count occurrences
    word_counts = {}
    for word in words:
        if word in word_counts:
            word_counts[word] += 1
        else:
            word_counts[word] = 1
    
    # Get top topics
    top_topics = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Calculate statistics
    total_sections = len(data['headings'])
    total_paragraphs = len(data['paragraphs'])
    total_list_items = len(data['list_items'])
    total_tables = len(data['tables'])
    
    return {
        'financial_data': financial_data,
        'top_topics': top_topics,
        'total_sections': total_sections,
        'total_paragraphs': total_paragraphs,
        'total_list_items': total_list_items,
        'total_tables': total_tables,
        'last_updated': data.get('last_updated', datetime.datetime.now().isoformat())
    }

# Helper function to create pie charts from table data
def create_pie_chart_for_table(df, table_index):
    """Create an enhanced pie chart for a table with better visualization and organization"""
    # Find numeric columns
    numeric_cols = []
    for col in df.columns:
        # Check if column contains numeric values or values with currency/unit indicators
        numeric_values = 0
        for val in df[col]:
            if val and isinstance(val, str):
                # Check for numeric values with or without currency symbols and units
                match = re.search(r'(?:€?\s*)?([-+]?\d[\d.,]*\s*(?:miljoen|mln|k|duizend)?)', val)
                if match:
                    numeric_values += 1
        
        # If more than 30% of values are numeric, consider it a numeric column
        if numeric_values > len(df) * 0.3:
            numeric_cols.append(col)
    
    # If we have numeric columns, create pie charts
    if numeric_cols:
        # Choose the best column for visualization (the one with most non-zero values)
        best_col = None
        max_non_zero = 0
        
        for col in numeric_cols:
            non_zero_count = 0
            for val in df[col]:
                if val and isinstance(val, str):
                    # Extract numeric value
                    match = re.search(r'(?:€?\s*)?([-+]?\d[\d.,]*\s*(?:miljoen|mln|k|duizend)?)', val)
                    if match and match.group(1):
                        # Clean and convert the value
                        num_str = match.group(1).replace('.', '').replace(',', '.')
                        
                        # Handle units (miljoen, duizend, etc.)
                        multiplier = 1
                        if 'miljoen' in num_str or 'mln' in num_str:
                            multiplier = 1000000
                            num_str = re.sub(r'\s*(?:miljoen|mln).*', '', num_str)
                        elif 'duizend' in num_str or 'k' in num_str:
                            multiplier = 1000
                            num_str = re.sub(r'\s*(?:duizend|k).*', '', num_str)
                        
                        try:
                            value = float(num_str) * multiplier
                            if value != 0:
                                non_zero_count += 1
                        except ValueError:
                            pass
            
            if non_zero_count > max_non_zero:
                max_non_zero = non_zero_count
                best_col = col
        
        if best_col:
            # Extract label column (usually the first non-numeric column)
            label_col = None
            for col in df.columns:
                if col not in numeric_cols:
                    label_col = col
                    break
            
            # If no suitable label column found, use the row index
            if not label_col:
                df['row_index'] = [f"Rij {i+1}" for i in range(len(df))]
                label_col = 'row_index'
            
            # Prepare data for pie chart
            labels = []
            values = []
            hover_text = []
            
            for i, row in df.iterrows():
                label = row[label_col]
                
                # Skip rows with empty or numeric-only labels
                if not label or (isinstance(label, str) and re.match(r'^[-+]?\d+(\.\d+)?$', label.strip())):
                    continue
                
                # Extract and convert the value
                val = row[best_col]
                if val and isinstance(val, str):
                    match = re.search(r'(?:€?\s*)?([-+]?\d[\d.,]*\s*(?:miljoen|mln|k|duizend)?)', val)
                    if match and match.group(1):
                        # Clean and convert the value
                        num_str = match.group(1).replace('.', '').replace(',', '.')
                        
                        # Handle units (miljoen, duizend, etc.)
                        multiplier = 1
                        if 'miljoen' in num_str or 'mln' in num_str:
                            multiplier = 1000000
                            num_str = re.sub(r'\s*(?:miljoen|mln).*', '', num_str)
                        elif 'duizend' in num_str or 'k' in num_str:
                            multiplier = 1000
                            num_str = re.sub(r'\s*(?:duizend|k).*', '', num_str)
                        
                        try:
                            value = float(num_str) * multiplier
                            if value != 0:  # Skip zero values
                                labels.append(label)
                                values.append(value)
                                
                                # Format hover text
                                if value >= 1000000:
                                    hover_text.append(f"€ {value/1000000:.1f} miljoen")
                                elif value >= 1000:
                                    hover_text.append(f"€ {value/1000:.1f} duizend")
                                else:
                                    hover_text.append(f"€ {value:,.0f}")
                        except ValueError:
                            pass
            
            if labels and values:
                # Sort by value and limit to top categories
                sorted_data = sorted(zip(labels, values, hover_text), key=lambda x: x[1], reverse=True)
                
                # If we have too many slices, group the smallest ones
                if len(sorted_data) > 7:
                    # Take top 6 and group the rest as "Overig"
                    top_data = sorted_data[:6]
                    other_sum = sum(value for _, value, _ in sorted_data[6:])
                    
                    if other_sum > 0:
                        top_data.append(("Overig", other_sum, f"€ {other_sum/1000000:.1f} miljoen" if other_sum >= 1000000 else f"€ {other_sum:,.0f}"))
                    
                    sorted_data = top_data
                
                # Unzip the sorted data
                labels, values, hover_text = zip(*sorted_data)
                
                # Create the pie chart
                fig = go.Figure(data=[go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.4,
                    textinfo='percent',
                    textposition='inside',
                    textfont=dict(size=14, color='white'),
                    marker=dict(
                        colors=px.colors.qualitative.Bold,
                        line=dict(color='white', width=2)
                    ),
                    hovertemplate='%{label}<br>%{percent}<br>Bedrag: %{customdata}',
                    customdata=hover_text
                )])
                
                # Update layout
                fig.update_layout(
                    title=f"Verdeling van {best_col}",
                    title_font=dict(size=16),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,
                        xanchor="center",
                        x=0.5,
                        font=dict(size=12)
                    ),
                    margin=dict(l=20, r=20, t=50, b=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                
                return dcc.Graph(figure=fig)
            else:
                return html.Div([
                    html.P("Geen geschikte gegevens voor visualisatie")
                ])
        else:
            return html.Div([
                html.P("Onvoldoende numerieke gegevens voor visualisatie")
            ])
    else:
        return html.Div([
            html.P("Geen numerieke kolommen gevonden")
        ])

# Helper function to create a mindmap for the headings
def create_mindmap(headings):
    """Create a simplified mindmap visualization for the document headings"""
    # Create a graph
    G = nx.Graph()
    
    # Add nodes and edges
    parent_map = {}
    
    # Add root node
    root_id = "Voorjaarsnota 2024"
    G.add_node(root_id)
    
    # Track node levels for styling
    node_levels = {root_id: 0}
    
    # Process headings to create a hierarchical structure
    # Only include levels 1 and 2 for simplicity
    for i, heading in enumerate(headings):
        # Clean the heading text
        text = heading['text'].strip()
        if not text or heading['level'] > 2:  # Skip empty headings and levels > 2
            continue
        
        # Create a unique ID for this heading
        node_id = f"{i}_{text[:30]}"
        
        # Add the node to the graph
        G.add_node(node_id, label=text, level=heading['level'])
        node_levels[node_id] = heading['level']
        
        # Connect to parent
        if heading['level'] == 1:
            # Level 1 headings connect to root
            G.add_edge(root_id, node_id)
            parent_map[heading['level']] = node_id
        else:
            # Find the closest parent level
            parent_level = heading['level'] - 1
            while parent_level > 0 and parent_level not in parent_map:
                parent_level -= 1
            
            if parent_level in parent_map:
                G.add_edge(parent_map[parent_level], node_id)
            else:
                # If no parent found, connect to root
                G.add_edge(root_id, node_id)
            
            # Update parent map
            parent_map[heading['level']] = node_id
    
    # Calculate node positions using a more spaced layout
    pos = nx.spring_layout(G, k=1.0, iterations=100, seed=42)
    
    # Create node traces with different sizes and colors based on level
    node_traces = []
    edge_traces = []
    
    # Simplified color scheme based on node level
    colors = {
        0: '#E94E24',  # Root (Rotterdam red)
        1: '#005A9C',  # Level 1 (Rotterdam blue)
        2: '#7F3C8D',  # Level 2 (Purple)
    }
    
    # Larger node sizes for better visibility
    sizes = {
        0: 50,  # Root
        1: 40,  # Level 1
        2: 30,  # Level 2
    }
    
    # Create edges first so they appear behind nodes
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        
        # Get the level of the target node for edge color
        target_level = node_levels.get(edge[1], 2)
        edge_color = colors.get(target_level, '#A5AA99')
        
        # Create edge trace with thicker lines
        edge_trace = go.Scatter(
            x=[x0, x1], 
            y=[y0, y1],
            mode='lines',
            line=dict(width=3, color=edge_color, dash='solid'),
            hoverinfo='none',
            showlegend=False
        )
        edge_traces.append(edge_trace)
    
    # Process nodes by level to ensure proper layering
    for level in sorted(set(node_levels.values())):
        level_nodes = [node for node, node_level in node_levels.items() if node_level == level]
        
        # Node properties based on level
        node_color = colors.get(level, colors[2])
        node_size = sizes.get(level, sizes[2])
        
        # Create node trace for this level
        node_x = []
        node_y = []
        node_text = []
        node_info = []
        
        for node in level_nodes:
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            # Get the label if available, otherwise use the node ID
            if 'label' in G.nodes[node]:
                label = G.nodes[node]['label']
                # Truncate long labels for display but keep full text for hover
                display_label = label if len(label) < 30 else label[:27] + '...'
                node_text.append(display_label)
                node_info.append(label)
            else:
                node_text.append(node)
                node_info.append(node)
        
        # Create the node trace with larger text
        node_trace = go.Scatter(
            x=node_x, 
            y=node_y,
            mode='markers+text',
            marker=dict(
                symbol='circle',
                size=node_size,
                color=node_color,
                line=dict(width=2, color='white')
            ),
            text=node_text,
            hovertext=node_info,
            hoverinfo='text',
            textposition="bottom center",
            textfont=dict(
                family="Arial",
                size=14,  # Larger text
                color="black"
            ),
            showlegend=False
        )
        node_traces.append(node_trace)
    
    # Create the figure
    fig = go.Figure(data=edge_traces + node_traces)
    
    # Update layout for better readability
    fig.update_layout(
        title={
            'text': "Structuur van de Voorjaarsnota 2024",
            'font': {'size': 24, 'color': '#005A9C'},
            'x': 0.5,
            'xanchor': 'center'
        },
        showlegend=False,
        hovermode='closest',
        margin=dict(b=60, l=20, r=20, t=80),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=600,
        plot_bgcolor='rgba(255,255,255,0.9)',
        paper_bgcolor='rgba(255,255,255,0)',
        annotations=[
            dict(
                text="<span style='font-size:16px; font-weight:bold;'>Legenda:</span>",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.01, y=-0.08,
                font=dict(size=14, color="#333")
            ),
            dict(
                text="<i class='fas fa-circle' style='color:#E94E24;'></i> Hoofddocument",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.15, y=-0.08,
                font=dict(size=14, color="#333")
            ),
            dict(
                text="<i class='fas fa-circle' style='color:#005A9C;'></i> Hoofdstukken",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.4, y=-0.08,
                font=dict(size=14, color="#333")
            ),
            dict(
                text="<i class='fas fa-circle' style='color:#7F3C8D;'></i> Secties",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.65, y=-0.08,
                font=dict(size=14, color="#333")
            )
        ]
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

# Function to create financial chart
def create_financial_chart(financial_data):
    """Create a bar chart for financial data with improved visualization"""
    if not financial_data:
        return {
            'data': [],
            'layout': {
                'title': 'Geen financiële gegevens beschikbaar',
                'height': 400
            }
        }
    
    # Create a DataFrame for the chart
    df = pd.DataFrame(financial_data)
    
    # Group by category and sum amounts
    df_grouped = df.groupby('category')['amount'].sum().reset_index()
    
    # Sort by amount for better visualization
    df_grouped = df_grouped.sort_values('amount', ascending=False).head(8)  # Show top 8 categories
    
    # Format amounts for display (in millions for large numbers)
    df_grouped['display_amount'] = df_grouped['amount'].apply(lambda x: 
        f"{x/1000000:.1f} mln" if x >= 1000000 else 
        f"{x/1000:.1f} K" if x >= 1000 else 
        f"{x:.0f}")
    
    # Create the bar chart with improved styling
    fig = px.bar(
        df_grouped, 
        x='category', 
        y='amount',
        color='amount',
        color_continuous_scale=px.colors.sequential.Blues,
        labels={'amount': 'Bedrag (€)', 'category': 'Categorie'},
        text='display_amount',  # Show the formatted amount as text on the bars
        height=500
    )
    
    # Customize the layout for better readability
    fig.update_layout(
        title={
            'text': 'Financiële Gegevens per Categorie',
            'font': {'size': 24, 'color': '#005A9C'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='',
        yaxis_title='Bedrag (€)',
        plot_bgcolor='rgba(240,240,240,0.2)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial, sans-serif", size=14),
        margin=dict(l=40, r=40, t=80, b=120),  # Increased bottom margin for labels
        hoverlabel=dict(bgcolor="white", font_size=14),
        xaxis=dict(tickangle=-45)  # Angled labels for better readability
    )
    
    # Format the text on the bars
    fig.update_traces(
        textposition='outside',
        texttemplate='%{text:.0f}',
        marker_line_color='rgb(8,48,107)',
        marker_line_width=1.5,
        opacity=0.8,
        hovertemplate='<b>%{x}</b><br>€%{y:,.0f}<extra></extra>'
    )
    
    return fig

# Function to create financial pie chart
def create_financial_pie_chart(financial_data):
    """Create a pie chart for financial data with improved visualization"""
    if not financial_data:
        return {
            'data': [],
            'layout': {
                'title': 'Geen financiële gegevens beschikbaar',
                'height': 400
            }
        }
    
    # Create a DataFrame for the chart
    df = pd.DataFrame(financial_data)
    
    # Group by category and sum amounts
    df_grouped = df.groupby('category')['amount'].sum().reset_index()
    
    # Sort by amount for better visualization
    df_grouped = df_grouped.sort_values('amount', ascending=False)
    
    # If we have too many slices, group the smallest ones
    if len(df_grouped) > 5:
        top_df = df_grouped.iloc[:4]
        other_sum = df_grouped.iloc[4:]['amount'].sum()
        
        if other_sum > 0:
            other_df = pd.DataFrame({'category': ['Overig'], 'amount': [other_sum]})
            df_grouped = pd.concat([top_df, other_df])
    
    # Calculate total for percentage calculation
    total = df_grouped['amount'].sum()
    
    # Format amounts for display (in millions for large numbers)
    df_grouped['display_amount'] = df_grouped['amount'].apply(lambda x: 
        f"€{x/1000000:.1f} miljoen" if x >= 1000000 else 
        f"€{x/1000:.1f} duizend" if x >= 1000 else 
        f"€{x:.0f}")
    
    # Format total amount
    total_display = f"€{total/1000000:.1f} miljoen" if total >= 1000000 else f"€{total/1000:.1f} duizend" if total >= 1000 else f"€{total:.0f}"
    
    # Create the pie chart with improved styling
    fig = px.pie(
        df_grouped, 
        values='amount', 
        names='category',
        color_discrete_sequence=px.colors.qualitative.Bold,
        height=600,  # Increased height for better visibility
        custom_data=['display_amount']  # Include formatted amount for hover
    )
    
    # Customize the layout for better readability
    fig.update_layout(
        title={
            'text': 'Verdeling van Financiën',
            'font': {'size': 24, 'color': '#005A9C'},
            'x': 0.5,
            'xanchor': 'center'
        },
        legend_title='Categorieën',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial, sans-serif", size=14),
        margin=dict(l=20, r=20, t=80, b=20),
        hoverlabel=dict(bgcolor="white", font_size=14)
    )
    
    # Format the text on the pie slices to show percentage and amount
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>%{customdata[0]}<br>%{percent}<extra></extra>',
        marker=dict(line=dict(color='#FFFFFF', width=2)),
        pull=[0.05 if i == 0 else 0 for i in range(len(df_grouped))],  # Pull out the largest slice
        rotation=45  # Start angle to make the chart more balanced
    )
    
    # Add interactive annotations
    fig.add_annotation(
        x=0.5,
        y=-0.05,
        xref="paper",
        yref="paper",
        text=f"<i class='fas fa-info-circle'></i> Totaal: {total_display}",
        showarrow=False,
        font=dict(size=14, color="#005A9C", family="Arial, sans-serif"),
        align="center",
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="#005A9C",
        borderwidth=1,
        borderpad=4
    )
    
    return fig

# Function to create topics chart
def create_topics_chart(topics):
    """Create a bar chart for top topics"""
    if topics:
        topics_df = pd.DataFrame(topics, columns=['topic', 'count'])
        fig_topics = px.bar(
            topics_df, 
            x='topic', 
            y='count',
            title='Meest Voorkomende Onderwerpen',
            labels={'topic': 'Onderwerp', 'count': 'Aantal Vermeldingen'},
            color_discrete_sequence=['#E94E24']
        )
        fig_topics.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=40, r=40, t=40, b=80),
            xaxis_tickangle=-45
        )
    else:
        fig_topics = go.Figure()
        fig_topics.add_annotation(
            text="Geen onderwerpen beschikbaar",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    return fig_topics

# Initialize the Dash app
app = dash.Dash(__name__, title="Gemeente Rotterdam Voorjaarsnota 2024 Dashboard")

# Define the app layout with icons and better explanations
app.layout = html.Div([
    # Hidden interval component for auto-refresh
    dcc.Interval(
        id='interval-component',
        interval=300000,  # 5 minutes in milliseconds
        n_intervals=0
    ),
    
    # Header
    html.Div([
        html.H1([
            html.I(className="fas fa-landmark mr-2"),
            "Gemeente Rotterdam Voorjaarsnota 2024"
        ], className="dashboard-title"),
        
        html.P([
            html.I(className="fas fa-info-circle mr-2"),
            "Dit dashboard geeft inzicht in de Voorjaarsnota 2024 van de gemeente Rotterdam. Hieronder vindt u visualisaties van de belangrijkste onderwerpen en financiële gegevens."
        ], className="dashboard-description"),
        
        # Info cards at the top
        html.Div([
            html.Div([
                html.I(className="fas fa-chart-pie fa-2x", style={"color": "#005A9C"}),
                html.H3("Financiële Gegevens"),
                html.P("Overzicht van de budgetten en investeringen per categorie.")
            ], className="info-card"),
            html.Div([
                html.I(className="fas fa-project-diagram fa-2x", style={"color": "#005A9C"}),
                html.H3("Mindmap"),
                html.P("Visuele weergave van de structuur van de Voorjaarsnota.")
            ], className="info-card"),
            html.Div([
                html.I(className="fas fa-table fa-2x", style={"color": "#005A9C"}),
                html.H3("Tabellen"),
                html.P("Gedetailleerde informatie uit de tabellen in de Voorjaarsnota.")
            ], className="info-card"),
            html.Div([
                html.I(className="fas fa-tags fa-2x", style={"color": "#005A9C"}),
                html.H3("Onderwerpen"),
                html.P("De meest voorkomende onderwerpen in de Voorjaarsnota.")
            ], className="info-card")
        ], className="info-cards-container"),
        
        # Last updated info
        html.Div(id='last-updated', className="last-updated")
    ], className="dashboard-header"),
    
    # Interactive introduction to the Voorjaarsnota
    html.Div([
        html.H2([
            html.I(className="fas fa-book-open mr-2"),
            "Wat is de Voorjaarsnota?"
        ]),
        
        # Interactive explanation cards
        html.Div([
            # Card 1
            html.Div([
                html.Div([
                    html.I(className="fas fa-file-invoice-dollar fa-3x", style={"color": "#E94E24"})
                ], className="intro-icon"),
                html.Div([
                    html.H3("Financiële Rapportage"),
                    html.P("De Voorjaarsnota is een financiële rapportage waarin de gemeente Rotterdam de stand van zaken van de begroting presenteert en vooruitkijkt naar de rest van het jaar.")
                ], className="intro-content")
            ], className="intro-card"),
            
            # Card 2
            html.Div([
                html.Div([
                    html.I(className="fas fa-calendar-alt fa-3x", style={"color": "#005A9C"})
                ], className="intro-icon"),
                html.Div([
                    html.H3("Halfjaarlijkse Update"),
                    html.P("De nota wordt halverwege het jaar gepubliceerd en geeft inzicht in de financiële ontwikkelingen sinds de begroting werd vastgesteld.")
                ], className="intro-content")
            ], className="intro-card"),
            
            # Card 3
            html.Div([
                html.Div([
                    html.I(className="fas fa-chart-line fa-3x", style={"color": "#7F3C8D"})
                ], className="intro-icon"),
                html.Div([
                    html.H3("Beleidsaanpassingen"),
                    html.P("In de Voorjaarsnota worden ook voorstellen gedaan voor beleidsaanpassingen en worden nieuwe investeringen voorgesteld.")
                ], className="intro-content")
            ], className="intro-card"),
            
            # Card 4
            html.Div([
                html.Div([
                    html.I(className="fas fa-users fa-3x", style={"color": "#11A579"})
                ], className="intro-icon"),
                html.Div([
                    html.H3("Voor Burgers"),
                    html.P("Dit dashboard maakt de informatie uit de Voorjaarsnota toegankelijker voor burgers door complexe financiële gegevens visueel weer te geven.")
                ], className="intro-content")
            ], className="intro-card")
        ], className="intro-cards-container"),
        
        # Interactive timeline
        html.Div([
            html.H3([
                html.I(className="fas fa-clock mr-2"),
                "Tijdlijn Voorjaarsnota 2024"
            ], className="timeline-title"),
            
            html.Div([
                # Timeline item 1
                html.Div([
                    html.Div(className="timeline-dot"),
                    html.Div([
                        html.H4("Januari 2024"),
                        html.P("Start van het begrotingsjaar 2024")
                    ], className="timeline-content")
                ], className="timeline-item"),
                
                # Timeline item 2
                html.Div([
                    html.Div(className="timeline-dot"),
                    html.Div([
                        html.H4("Maart 2024"),
                        html.P("Voorbereiding en analyse voor de Voorjaarsnota")
                    ], className="timeline-content")
                ], className="timeline-item"),
                
                # Timeline item 3
                html.Div([
                    html.Div(className="timeline-dot active"),
                    html.Div([
                        html.H4("Mei 2024"),
                        html.P("Publicatie van de Voorjaarsnota 2024")
                    ], className="timeline-content active")
                ], className="timeline-item"),
                
                # Timeline item 4
                html.Div([
                    html.Div(className="timeline-dot"),
                    html.Div([
                        html.H4("Juni 2024"),
                        html.P("Bespreking in de gemeenteraad")
                    ], className="timeline-content")
                ], className="timeline-item"),
                
                # Timeline item 5
                html.Div([
                    html.Div(className="timeline-dot"),
                    html.Div([
                        html.H4("September 2024"),
                        html.P("Verwerking in de begroting voor 2025")
                    ], className="timeline-content")
                ], className="timeline-item")
            ], className="timeline-container")
        ], className="timeline-section")
    ], className="dashboard-section introduction-section"),
    
    # Financial charts section
    html.Div([
        html.H2([
            html.I(className="fas fa-euro-sign mr-2"),
            "Financiële Overzichten"
        ]),
        
        html.Div([
            html.Div([
                html.H3([
                    html.I(className="fas fa-chart-bar mr-2"),
                    "Financiële Gegevens per Categorie"
                ]),
                dcc.Graph(id='financial-chart')
            ], className="chart-column"),
            
            html.Div([
                html.H3([
                    html.I(className="fas fa-chart-pie mr-2"),
                    "Verdeling van Financiën"
                ]),
                dcc.Graph(id='financial-pie-chart')
            ], className="chart-column")
        ], className="two-column-layout"),
        
        html.Div([
            html.H3([
                html.I(className="fas fa-table mr-2"),
                "Financiële Tabel"
            ]),
            html.Div(id='financial-table')
        ], className="table-section")
    ], className="dashboard-section"),
    
    # Topics section
    html.Div([
        html.H2([
            html.I(className="fas fa-tags mr-2"),
            "Belangrijkste Onderwerpen"
        ]),
        dcc.Graph(id='topics-chart')
    ], className="dashboard-section"),
    
    # Mindmap section
    html.Div([
        html.H2([
            html.I(className="fas fa-project-diagram mr-2"),
            "Structuur van de Voorjaarsnota"
        ]),
        html.Div(id='headings-mindmap')
    ], className="dashboard-section"),
    
    # Statistics section
    html.Div([
        html.H2([
            html.I(className="fas fa-chart-line mr-2"),
            "Statistieken"
        ]),
        html.Div(id='statistics')
    ], className="dashboard-section"),
    
    # Tables section
    html.Div([
        html.H2([
            html.I(className="fas fa-table mr-2"),
            "Tabellen uit de Voorjaarsnota"
        ]),
        html.Div(id='tables-section')
    ], className="dashboard-section"),
    
    # Footer
    html.Div([
        html.P([
            html.I(className="fas fa-info-circle mr-2"),
            "Dit dashboard is ontwikkeld om de Voorjaarsnota 2024 van de gemeente Rotterdam toegankelijker te maken voor burgers."
        ]),
        html.P([
            html.I(className="fas fa-sync mr-2"),
            "De gegevens worden automatisch elke 5 minuten bijgewerkt."
        ])
    ], className="dashboard-footer")
], className="dashboard-container")

# Add CSS for the layout
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <!-- Add Font Awesome for icons -->
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f5f5f5;
            }
            
            .dashboard-container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .dashboard-header {
                text-align: center;
                margin-bottom: 30px;
                background-color: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .dashboard-title {
                color: #005A9C;
                margin-bottom: 10px;
            }
            
            .dashboard-description {
                text-align: left;
                margin: 20px 0;
                line-height: 1.6;
                color: #555;
            }
            
            .info-cards-container {
                display: flex;
                flex-wrap: wrap;
                justify-content: space-around;
                margin: 20px 0;
            }
            
            .info-card {
                background-color: #f9f9f9;
                border-radius: 8px;
                padding: 20px;
                margin: 10px;
                width: calc(25% - 20px);
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                text-align: center;
                transition: transform 0.3s, box-shadow 0.3s;
            }
            
            .info-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            
            .info-card i {
                font-size: 36px;
                margin-bottom: 15px;
                color: #005A9C;
            }
            
            .info-card h3 {
                margin-top: 0;
                color: #333;
                font-size: 18px;
            }
            
            .info-card p {
                color: #666;
                font-size: 14px;
            }
            
            .dashboard-section {
                margin-bottom: 40px;
                background-color: white;
                border-radius: 8px;
                padding: 25px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .dashboard-section h2 {
                color: #005A9C;
                margin-top: 0;
                margin-bottom: 20px;
                border-bottom: 2px solid #f0f0f0;
                padding-bottom: 10px;
            }
            
            .chart-column {
                flex: 1 1 45%;
                min-width: 300px;
                margin: 10px;
            }
            
            .two-column-layout {
                display: flex;
                flex-wrap: wrap;
                justify-content: space-around;
            }
            
            .table-section {
                margin-top: 30px;
            }
            
            .statistics-container {
                display: flex;
                flex-wrap: wrap;
                justify-content: space-around;
                margin-top: 20px;
            }
            
            .stat-item {
                text-align: center;
                background-color: #f9f9f9;
                border-radius: 8px;
                padding: 20px;
                margin: 10px;
                width: calc(20% - 20px);
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                transition: transform 0.3s;
            }
            
            .stat-item:hover {
                transform: scale(1.05);
                background-color: #f0f0f0;
            }
            
            .stat-value {
                font-size: 24px;
                font-weight: bold;
                color: #E94E24;
                margin: 10px 0;
            }
            
            .stat-label {
                font-size: 14px;
                color: #666;
                margin: 5px 0 0;
            }
            
            .table-container {
                margin-bottom: 40px;
                border: 1px solid #f0f0f0;
                border-radius: 8px;
                padding: 25px;
                background-color: white;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                transition: transform 0.3s;
            }
            
            .table-container:hover {
                transform: translateY(-5px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            
            .table-title {
                color: #005A9C;
                margin-top: 0;
                margin-bottom: 15px;
                font-size: 20px;
            }
            
            .table-description {
                color: #666;
                margin-bottom: 20px;
                font-size: 14px;
                line-height: 1.5;
            }
            
            .section-subtitle {
                color: #005A9C;
                margin-top: 0;
                margin-bottom: 15px;
                font-size: 16px;
            }
            
            .table-chart-container {
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                align-items: flex-start;
            }
            
            .table-view {
                flex: 1 1 55%;
                min-width: 300px;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            }
            
            .chart-view {
                flex: 1 1 40%;
                min-width: 300px;
                background-color: #f9f9f9;
                border-radius: 8px;
                padding: 15px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            }
            
            .dashboard-footer {
                background-color: #005A9C;
                color: white;
                padding: 30px;
                border-radius: 8px;
                margin-top: 30px;
                text-align: center;
            }
            
            .dashboard-footer p {
                margin-bottom: 10px;
                font-size: 14px;
                line-height: 1.6;
            }
            
            .last-updated {
                margin-top: 15px;
                font-size: 14px;
                color: #888;
                font-style: italic;
            }
            
            /* New styles for introduction section */
            .introduction-section {
                padding: 30px;
            }
            
            .intro-cards-container {
                display: flex;
                flex-wrap: wrap;
                justify-content: space-between;
                margin: 30px 0;
            }
            
            .intro-card {
                display: flex;
                background-color: #f9f9f9;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
                width: calc(50% - 15px);
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                transition: transform 0.3s, box-shadow 0.3s;
            }
            
            .intro-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            
            .intro-icon {
                flex: 0 0 80px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .intro-content {
                flex: 1;
                padding-left: 15px;
            }
            
            .intro-content h3 {
                margin-top: 0;
                color: #333;
                font-size: 18px;
            }
            
            .intro-content p {
                color: #666;
                font-size: 14px;
                line-height: 1.5;
            }
            
            /* Timeline styles */
            .timeline-section {
                margin-top: 40px;
            }
            
            .timeline-title {
                color: #005A9C;
                margin-bottom: 20px;
            }
            
            .timeline-container {
                position: relative;
                padding: 20px 0;
            }
            
            .timeline-container:before {
                content: '';
                position: absolute;
                top: 0;
                left: 50px;
                height: 100%;
                width: 4px;
                background: #005A9C;
                opacity: 0.3;
            }
            
            .timeline-item {
                position: relative;
                margin-bottom: 30px;
                padding-left: 70px;
            }
            
            .timeline-dot {
                position: absolute;
                left: 46px;
                top: 10px;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background: #005A9C;
                transform: translateX(-50%);
            }
            
            .timeline-dot.active {
                background: #E94E24;
                width: 16px;
                height: 16px;
                box-shadow: 0 0 0 4px rgba(233, 78, 54, 0.2);
            }
            
            .timeline-content {
                background: #f9f9f9;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            }
            
            .timeline-content.active {
                background: #fff;
                border-left: 4px solid #E94E24;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            
            .timeline-content h4 {
                margin-top: 0;
                color: #333;
                font-size: 16px;
            }
            
            .timeline-content p {
                margin-bottom: 0;
                color: #666;
                font-size: 14px;
            }
            
            /* Responsive adjustments */
            @media (max-width: 768px) {
                .two-column-layout {
                    flex-direction: column;
                }
                
                .chart-column {
                    flex: 1 1 100%;
                }
                
                .info-cards-container {
                    flex-direction: column;
                }
                
                .info-card {
                    width: 100%;
                    margin: 10px 0;
                }
                
                .table-chart-container {
                    flex-direction: column;
                }
                
                .table-view, .chart-view {
                    flex: 1 1 100%;
                }
                
                .stat-item {
                    width: calc(50% - 20px);
                }
                
                .intro-card {
                    width: 100%;
                }
            }
            
            /* Additional styles for better visual hierarchy */
            .mr-2 {
                margin-right: 8px;
            }
            
            .fas {
                vertical-align: middle;
            }
        </style>
        {%scripts%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Define callback to update the dashboard
@app.callback(
    [
        dash.dependencies.Output('financial-chart', 'figure'),
        dash.dependencies.Output('financial-pie-chart', 'figure'),
        dash.dependencies.Output('topics-chart', 'figure'),
        dash.dependencies.Output('statistics', 'children'),
        dash.dependencies.Output('financial-table', 'children'),
        dash.dependencies.Output('headings-mindmap', 'children'),
        dash.dependencies.Output('tables-section', 'children'),
        dash.dependencies.Output('last-updated', 'children')
    ],
    [dash.dependencies.Input('interval-component', 'n_intervals')]
)
def update_dashboard(n_intervals):
    # Scrape and process data
    data = scrape_data()
    metrics = process_data(data)
    
    # Create financial chart
    financial_chart = create_financial_chart(metrics['financial_data'])
    
    # Create financial pie chart
    financial_pie_chart = create_financial_pie_chart(metrics['financial_data'])
    
    # Create topics chart
    topics_chart = create_topics_chart(metrics['top_topics'])
    
    # Create statistics
    statistics_items = [
        html.Div([
            html.I(className="fas fa-book fa-2x", style={"color": "#005A9C"}),
            html.P(metrics['total_sections'], className="stat-value"),
            html.P("Secties", className="stat-label")
        ], className="stat-item"),
        html.Div([
            html.I(className="fas fa-paragraph fa-2x", style={"color": "#005A9C"}),
            html.P(metrics['total_paragraphs'], className="stat-value"),
            html.P("Paragrafen", className="stat-label")
        ], className="stat-item"),
        html.Div([
            html.I(className="fas fa-list-ul fa-2x", style={"color": "#005A9C"}),
            html.P(metrics['total_list_items'], className="stat-value"),
            html.P("Lijstitems", className="stat-label")
        ], className="stat-item"),
        html.Div([
            html.I(className="fas fa-table fa-2x", style={"color": "#005A9C"}),
            html.P(metrics['total_tables'], className="stat-value"),
            html.P("Tabellen", className="stat-label")
        ], className="stat-item"),
        html.Div([
            html.I(className="fas fa-euro-sign fa-2x", style={"color": "#005A9C"}),
            html.P(len(metrics['financial_data']), className="stat-value"),
            html.P("Financiële Items", className="stat-label")
        ], className="stat-item")
    ]
    
    # Create financial table
    if metrics['financial_data']:
        # Create a DataFrame from the financial data
        df = pd.DataFrame(metrics['financial_data'])
        
        # Rename columns for better understanding
        column_mapping = {
            'description': 'Beschrijving',
            'amount': 'Bedrag'
        }
        df = df.rename(columns=column_mapping)
        
        # Remove the source column if it exists
        if 'source' in df.columns:
            df = df.drop(columns=['source'])
        
        financial_table = [
            html.H3([
                html.I(className="fas fa-euro-sign mr-2", style={"color": "#005A9C"}),
                "Financiële Gegevens"
            ]),
            dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{'name': col, 'id': col} for col in df.columns],
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '10px',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'minWidth': '100px',
                    'maxWidth': '300px',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis'
                },
                style_header={
                    'backgroundColor': '#005A9C',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'textAlign': 'left',
                    'padding': '12px'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#f9f9f9'
                    }
                ],
                page_size=10,
                style_as_list_view=True,
                tooltip_delay=0,
                tooltip_duration=None
            )
        ]
    else:
        financial_table = [
            html.Div([
                html.I(className="fas fa-exclamation-circle fa-3x", style={"color": "#E94E24"}),
                html.P("Geen financiële gegevens beschikbaar")
            ], style={"textAlign": "center", "padding": "40px"})
        ]
    
    # Create mindmap
    mindmap = create_mindmap(data['headings'])
    
    # Create tables section
    tables_section = []
    for i, table in enumerate(data['tables']):
        if table['headers'] or table['rows']:
            # Create a DataFrame from the table data
            if table['headers'] and table['rows']:
                # If there are headers and rows, use headers as column names
                # Ensure all rows have the same length as headers
                uniform_rows = []
                for row in table['rows']:
                    # Pad or truncate row to match headers length
                    if len(row) < len(table['headers']):
                        uniform_rows.append(row + [''] * (len(table['headers']) - len(row)))
                    else:
                        uniform_rows.append(row[:len(table['headers'])])
                
                df = pd.DataFrame(uniform_rows, columns=table['headers'])
            elif table['rows']:
                # If no headers but rows exist, use generic column names
                max_cols = max([len(row) for row in table['rows']])
                columns = [f"Column {i+1}" for i in range(max_cols)]
                
                uniform_rows = []
                for row in table['rows']:
                    # Pad or truncate row to match max columns
                    if len(row) < max_cols:
                        uniform_rows.append(row + [''] * (max_cols - len(row)))
                    else:
                        uniform_rows.append(row[:max_cols])
                
                df = pd.DataFrame(uniform_rows, columns=columns)
            else:
                # Empty table with just headers
                df = pd.DataFrame(columns=table['headers'])
            
            # Generate a meaningful title based on table content
            title = "Gegevens"
            if table['headers']:
                # Try to find a meaningful title from the headers
                potential_titles = [h for h in table['headers'] if len(h) > 3 and not re.match(r'^[-+]?\d+(\.\d+)?$', h)]
                if potential_titles:
                    title = potential_titles[0]
            
            # Create a container for this table
            table_container = html.Div([
                html.H3([
                    html.I(className="fas fa-table mr-2", style={"color": "#005A9C"}),
                    f"Tabel {i+1}: {title}"
                ], className="table-title"),
                
                # Add a description based on the headers
                html.P([
                    html.I(className="fas fa-info-circle mr-2"),
                    f"Deze tabel toont informatie over {', '.join(table['headers'][:3]) if table['headers'] else 'verschillende gegevens'} uit de Voorjaarsnota."
                ], className="table-description"),
                
                # Side by side layout for table and chart
                html.Div([
                    # Table view
                    html.Div([
                        html.H4([
                            html.I(className="fas fa-list mr-2"),
                            "Tabelgegevens"
                        ], className="section-subtitle"),
                        dash_table.DataTable(
                            data=df.to_dict('records'),
                            columns=[{'name': col, 'id': col} for col in df.columns],
                            style_table={'overflowX': 'auto'},
                            style_cell={
                                'textAlign': 'left',
                                'padding': '10px',
                                'whiteSpace': 'normal',
                                'height': 'auto',
                                'minWidth': '100px',
                                'maxWidth': '300px',
                                'overflow': 'hidden',
                                'textOverflow': 'ellipsis'
                            },
                            style_header={
                                'backgroundColor': '#005A9C',
                                'color': 'white',
                                'fontWeight': 'bold',
                                'textAlign': 'left',
                                'padding': '12px'
                            },
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': '#f9f9f9'
                                }
                            ],
                            page_size=10,
                            style_as_list_view=True,
                            tooltip_delay=0,
                            tooltip_duration=None
                        )
                    ], className="table-view"),
                    
                    # Chart view
                    html.Div([
                        html.H4([
                            html.I(className="fas fa-chart-pie mr-2"),
                            "Visualisatie"
                        ], className="section-subtitle"),
                        create_pie_chart_for_table(df, i)
                    ], className="chart-view")
                ], className="table-chart-container")
            ], className="table-container")
            
            tables_section.append(table_container)
    
    if not tables_section:
        tables_section = [
            html.Div([
                html.I(className="fas fa-exclamation-circle fa-3x", style={"color": "#E94E24"}),
                html.P("Geen tabellen beschikbaar in de Voorjaarsnota")
            ], style={"textAlign": "center", "padding": "40px"})
        ]
    
    # Last updated
    try:
        last_updated = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        last_updated_div = html.P(f"Laatst bijgewerkt: {last_updated}", className="last-updated")
    except:
        last_updated_div = html.P("Laatst bijgewerkt: onbekend", className="last-updated")
    
    return financial_chart, financial_pie_chart, topics_chart, statistics_items, financial_table, mindmap, tables_section, last_updated_div

# Run the app
if __name__ == '__main__':
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Run the app
    app.run_server(debug=True, port=9053)
else:
    # For production deployment
    server = app.server

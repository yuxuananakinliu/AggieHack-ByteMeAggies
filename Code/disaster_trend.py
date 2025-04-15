!pip install supabase
!pip install getapi

import pandas as pd
from supabase import create_client
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt
import folium
from folium.plugins import HeatMap

def ext_api(file_name: str)->dict[str, str]:
    api_dict = {}
    with open(file_name, 'r') as file:
        for line in file:
            key, value = line.strip().split('=', 1)
            api_dict[key.strip()] = value.strip()
    return api_dict

def create_conn(apifile:str):
    '''Create connection to Supabase database via API call'''
    supaapi = ext_api(apifile)
    sb_client = create_client(supaapi['URL'], supaapi['APIKEY'])
    return sb_client

def rolling_query(api_file:str, table_name:str, target_col:str='*', query_limit:int=1000)->pd.DataFrame:
    '''Query data from Supabase in batches, return all columns by default'''
    all_rows = []
    offset = 0
    sb_client = create_conn(api_file)

    while True:
        response = sb_client.table(table_name).select(
            target_col
        ).range(offset, offset+query_limit-1).execute()
        if not response.data:
            break
        all_rows.extend(response.data)
        offset += query_limit

    return pd.DataFrame(all_rows)

disaster = rolling_query("supabaseapi.txt", "disaster_events")

disaster.head()

## Trend Analysis
### Using ARIMA model for Time-Series Forecasting
disaster['date'] = pd.to_datetime(disaster['date'])

# Filter data based on the disaster type (e.g., earthquake, fire, etc.)
disaster_types = disaster['disaster_type'].unique()
disaster_types

# Making the subset of data for each disaster type
disaster_data = {disaster_type: disaster[disaster['disaster_type'] == disaster_type] for disaster_type in disaster_types}

# Display the subsets for each disaster type
for disaster_type in disaster_types:
    print(f"Data for {disaster_type}:\n", disaster_data[disaster_type].head(), "\n")

# Function to forecast and visualize predictions for a disaster type and export the results
def forecast_and_plot(disaster_data, disaster_type, target_column, output_filename):
    # Prepare the time-series data (e.g., severity, casualties, etc.)
    ts_data = disaster_data[target_column]

    # Split into train and test sets
    train_size = int(len(ts_data) * 0.8)
    train, test = ts_data[:train_size], ts_data[train_size:]

    # ARIMA Model
    model = ARIMA(train, order=(5, 1, 0))
    model_fit = model.fit()

    # Make predictions
    predictions = model_fit.forecast(steps=len(test))

    # Create a DataFrame with the actual and predicted values
    prediction_df = pd.DataFrame({
        'Date': test.index,
        'Actual': test.values,
        'Predicted': predictions
    })

    # Export the predictions to a CSV file
    prediction_df.to_csv(output_filename, index=False)

    # Plot the actual vs predicted
    plt.figure(figsize=(10, 6))
    plt.plot(test.index, test.values, label='Actual')
    plt.plot(test.index, predictions, label='Predicted', color='red')
    plt.title(f'ARIMA Prediction for {disaster_type} - {target_column}')
    plt.xlabel('Date')
    plt.ylabel(target_column)
    plt.legend()
    plt.show()

# For each disaster type, forecast severity, casualties, economic loss, and duration
for disaster_type, subset in disaster_data.items():
    for target_column in ['severity', 'casualties', 'economic_loss_million_usd', 'duration_hours']:
        output_filename = f'{disaster_type}_{target_column}_predictions.csv'
        forecast_and_plot(subset, disaster_type, target_column, output_filename)


### Map Visualization for Disaster Distribution
# Create a map centered on the average location of the disasters
avg_lat = disaster['latitude'].mean()
avg_lon = disaster['longitude'].mean()

# Create a base map
disaster_map = folium.Map(location=[avg_lat, avg_lon], zoom_start=6)

# Define a color map for each disaster type
disaster_colors = {
    'earthquake': 'red',
    'fire': 'orange',
    'industrial accident': 'blue',
    'flood': 'green',
    'hospital overload': 'purple'
}

# Add markers for each disaster event
for _, row in disaster.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=5,
        color=disaster_colors.get(row['disaster_type'], 'gray'),
        fill=True,
        fill_color=disaster_colors.get(row['disaster_type'], 'gray'),
        fill_opacity=0.6
    ).add_to(disaster_map)

# Display the map
disaster_map.save("disaster_map.html")

#### Heatmap for disasters
# Create a heatmap of the disaster locations
heat_data = [[row['latitude'], row['longitude']] for _, row in disaster.iterrows()]

# Create the heatmap on the same map
heat_map = folium.Map(location=[avg_lat, avg_lon], zoom_start=6)
HeatMap(heat_data).add_to(heat_map)

# Display the heatmap
heat_map.save("disaster_heatmap.html")

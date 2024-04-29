import json
import requests
from datetime import datetime, timedelta

class WeatherLog:
    def __init__(self):
        self.data = {}
        self.load_from_json()

    def save_day_data(self, date, weather_data):
        self.data[date] = weather_data
        self.save_to_json()

    def get_day_data(self, date):
        return self.data.get(date, None)

    def save_to_json(self):
        with open('weather_data.json', 'w') as f:
            json.dump(self.data, f, indent=4)

    def load_from_json(self):
        try:
            with open('weather_data.json', 'r') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {}

class YRWeather:
    def __init__(self):
        self.headers = {
            'User-Agent': 'WeatherLogApp/1.0 (joseke@uia.no)'
        }

    def fetch_weather_data(self, latitude, longitude, date):
        formatted_date = datetime.strptime(date, '%d-%m-%Y').strftime('%Y-%m-%dT12:00:00Z')
        url = f'https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={latitude}&lon={longitude}&time={formatted_date}'

        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            for timeslot in data['properties']['timeseries']:
                timeslot_time = datetime.fromisoformat(timeslot['time'].replace('Z', '+00:00'))
                if timeslot_time.date() == datetime.strptime(date, '%d-%m-%Y').date():
                    details = timeslot['data']['instant']['details']
                    return {
                        'temperature': details['air_temperature'],
                        'wind_speed': details['wind_speed'],
                        'precipitation': timeslot['data']['next_1_hours']['details']['precipitation_amount'] if 'next_1_hours' in timeslot['data'] else 0
                    }
        else:
            print(f"Failed to fetch data from YR API. Status code: {response.status_code}")
            return None

class WeatherApp:
    def __init__(self):
        self.weather_log = WeatherLog()
        self.yr_weather = YRWeather()

    def run(self):
        self.weather_log.load_from_json()
        while True:
            print("Welcome to the Weather Log App!")
            print("1. Enter weather data for a day")
            print("2. View weather report for a day")
            print("3. View weather report for a week")
            print("4. View weather report for a month")
            print("5. Exit")

            choice = input("Enter your choice (1-5): ")

            if choice == '1':
                date = input("Enter the date (DD-MM-YYYY): ")
                temperature = float(input("Enter the temperature: "))
                precipitation = float(input("Enter the precipitation: "))
                wind_speed = float(input("Enter the wind speed: "))
                weather_data = {
                    'temperature': temperature,
                    'precipitation': precipitation,
                    'wind_speed': wind_speed
                }
                self.weather_log.save_day_data(date, weather_data)
                print("Weather data saved successfully.")

            elif choice == '2':
                date = input("Enter the date (DD-MM-YYYY): ")
                day_data = self.weather_log.get_day_data(date)
                if day_data:
                    print(f"Weather data for {date}:")
                    print(day_data)
                else:
                    print(f"No weather data found for {date}.")

            elif choice == '3' or choice == '4':
                latitude = input("Enter the latitude: ")
                longitude = input("Enter the longitude: ")
                if choice == '3':
                    week_number = input("Enter the week number (1-52): ")
                    year = int(input("Enter the year (e.g., 2024): "))
                    start_date = datetime.strptime(f'{year}-W{int(week_number)-1}-1', "%Y-W%W-%w").date()
                    end_date = start_date + timedelta(days=6)
                    print(f"Weather report for week number {week_number}:")
                    for single_date in (start_date + timedelta(n) for n in range(7)):
                        date_str = single_date.strftime('%d-%m-%Y')
                        print(f"Date: {date_str}")

                        yr_data = self.yr_weather.fetch_weather_data(latitude, longitude, date_str)
                        if yr_data:
                            print("YR Weather Data:")
                            print(f"Temperature: {yr_data['temperature']}°C")
                            print(f"Wind Speed: {yr_data['wind_speed']} m/s")
                            print(f"Precipitation: {yr_data['precipitation']} mm")
                        else:
                            print("No YR data available for this date.")

                elif choice == '4':
                    month = int(input("Enter the month number (1-12): "))
                    year = int(input("Enter the year (e.g., 2024): "))
                    start_date = datetime(year, month, 1)
                    end_date = datetime(year, month + 1, 1) - timedelta(days=1)
                    print(f"Weather report for {start_date.strftime('%B')} {year}:")
                    while start_date <= end_date:
                        date_str = start_date.strftime('%d-%m-%Y')
                        print(f"Date: {date_str}")
                        yr_data = self.yr_weather.fetch_weather_data(latitude, longitude, date_str)
                        if yr_data:
                            print("YR Weather Data:")
                            print(f"Temperature: {yr_data['temperature']}°C")
                            print(f"Wind Speed: {yr_data['wind_speed']} m/s")
                            print(f"Precipitation: {yr_data['precipitation']} mm")
                        else:
                            print("No YR data available for this date.")
                        start_date += timedelta(days=1)

            elif choice == '5':
                print("Exiting Weather Log App...")
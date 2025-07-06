import tkinter as tk
from PIL import Image, ImageTk
import requests
from datetime import datetime

# ====== CONFIG ======
API_KEY = "ff23c8ca55e474b25a4351a76f6def9a"  # Replace with your actual OpenWeatherMap API key

ICON_MAP = {
    "01": "sun.png",
    "02": "cloud.png",
    "03": "cloud.png",
    "04": "cloud.png",
    "09": "rain.png",
    "10": "rain.png",
    "11": "storm.png",
    "13": "snow.png",
    "50": "cloud.png"
}

# GUI setup
root = tk.Tk()
root.title("Weather Tracker")
root.geometry("500x650")
root.configure(bg="skyblue")  # Changed background to sky blue

HEADER_FONT = ("Helvetica", 24, "bold")
TEMP_FONT = ("Helvetica", 44)
TEXT_FONT = ("Helvetica", 12)

# Label for instruction
instruction_label = tk.Label(root, text="Enter City Name:", font=("Helvetica", 14), bg="skyblue", fg="black")
instruction_label.pack(pady=(10, 0))

# City Entry
city_entry = tk.Entry(root, font=("Helvetica", 14))
city_entry.pack(pady=5)
city_entry.insert(0, "")  # Start with blank

# Labels
city_label = tk.Label(root, text="", font=HEADER_FONT, bg="skyblue", fg="black")
city_label.pack()

main_icon_label = tk.Label(root, bg="skyblue")
main_icon_label.pack()

temp_frame = tk.Frame(root, bg="skyblue")
temp_frame.pack()

range_label = tk.Label(root, text="", font=TEXT_FONT, bg="skyblue", fg="black")
range_label.pack()

condition_label = tk.Label(root, text="", font=TEXT_FONT, bg="skyblue", fg="black")
condition_label.pack(pady=5)

divider = tk.Frame(root, height=2, bd=0, relief="sunken", bg="gray")
divider.pack(fill="x", padx=20, pady=10)

forecast_frame = tk.Frame(root, bg="skyblue")
forecast_frame.pack(pady=10)

# Global holder for temp_label
temp_label = None


def get_icon_file(code):
    return ICON_MAP.get(code[:2], "cloud.png")


def update_weather(event=None):  # Accept optional event param for key binding
    global temp_label

    city = city_entry.get().strip()
    if not city:
        city_label.config(text="Please enter a city.")
        return

    current_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"

    current = requests.get(current_url).json()
    forecast = requests.get(forecast_url).json()

    # Current weather
    city_label.config(text=current['name'])
    temp = round(current['main']['temp'])

    if temp_label is None:
        temp_label = tk.Label(temp_frame, text=f"{temp}°", font=TEMP_FONT, bg="skyblue", fg="black")
        temp_label.pack()
    else:
        temp_label.config(text=f"{temp}°")

    range_label.config(
        text=f"{round(current['main']['temp_min'])}° / {round(current['main']['temp_max'])}°")
    condition = current['weather'][0]['description'].capitalize()
    condition_label.config(text=condition)

    icon_code = current['weather'][0]['icon']
    icon_file = get_icon_file(icon_code)
    icon_img = Image.open(icon_file).resize((100, 100))
    icon_photo = ImageTk.PhotoImage(icon_img)
    main_icon_label.config(image=icon_photo)
    main_icon_label.image = icon_photo

    # Clear old forecast
    for widget in forecast_frame.winfo_children():
        widget.destroy()

    # Forecast
    daily = {}
    for entry in forecast['list']:
        dt = datetime.fromtimestamp(entry['dt'])
        day = dt.strftime('%a')
        if day not in daily:
            daily[day] = {
                'temp_min': entry['main']['temp_min'],
                'temp_max': entry['main']['temp_max'],
                'icon': entry['weather'][0]['icon']
            }
        else:
            daily[day]['temp_min'] = min(daily[day]['temp_min'], entry['main']['temp_min'])
            daily[day]['temp_max'] = max(daily[day]['temp_max'], entry['main']['temp_max'])

    for i, (day, data) in enumerate(list(daily.items())[:5]):
        frame = tk.Frame(forecast_frame, bg="skyblue")
        frame.pack(side=tk.LEFT, padx=10)

        icon_file = get_icon_file(data['icon'])
        icon_img = Image.open(icon_file).resize((40, 40))
        icon_photo = ImageTk.PhotoImage(icon_img)

        icon_label = tk.Label(frame, image=icon_photo, bg="skyblue")
        icon_label.image = icon_photo
        icon_label.pack()

        day_label = tk.Label(frame, text=day, font=TEXT_FONT, bg="skyblue", fg="black")
        day_label.pack()

        temp_range = f"{round(data['temp_max'])}/{round(data['temp_min'])}"
        temp_label_f = tk.Label(frame, text=temp_range, font=TEXT_FONT, bg="skyblue", fg="black")
        temp_label_f.pack()


# Button to fetch weather
tk.Button(root, text="Get Weather", command=update_weather, font=TEXT_FONT).pack(pady=10)

# Bind Enter key to trigger weather update
city_entry.bind("<Return>", update_weather)

root.mainloop()

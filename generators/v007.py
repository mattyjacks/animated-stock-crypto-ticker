import tkinter as tk
from tkinter import ttk, Text
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import yfinance as yf
import pandas as pd
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageDraw
import moviepy.editor as mpy
import datetime
from tqdm import tqdm
import matplotlib.dates as mdates

# Helper function to get ordinal day suffix
def get_ordinal(n):
    return "%d%s" % (n, "th" if 4 <= n <= 20 or 24 <= n <= 30 else ["st", "nd", "rd"][n % 10 - 1])

# Helper function to format date
def format_date(date_str):
    date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    month = date_obj.strftime('%B')
    day = get_ordinal(date_obj.day)
    year = date_obj.year
    return f"{month} {day} {year}"

# Function to generate the animation
def generate_animation():
    ticker_type = ticker_type_var.get()
    ticker = ticker_entry.get()
    start_date = start_entry.get()
    end_date = end_entry.get()
    skip_days = int(skip_days_entry.get() or 0)
    include_start_date = include_start_var.get()
    include_end_date = include_end_var.get()
    custom_text = custom_text_box.get("1.0", tk.END).strip()
    x_ticks_interval = int(x_ticks_entry.get() or 1)
    y_ticks_interval = int(y_ticks_entry.get() or 10)
    chart_height_pct = int(chart_height_entry.get() or 100) / 100
    watermark_text = watermark_entry.get()
    watermark_color = watermark_color_entry.get()
    cut_initial_frames = cut_initial_frames_var.get()

    # Fetch stock/crypto data
    data = yf.download(ticker, start=start_date, end=end_date)

    # Apply skip days
    data = data[::skip_days+1]

    # Cut out initial frames if selected
    if cut_initial_frames:
        data = data.iloc[skip_days+1:]

    # Format the start and end dates
    formatted_start_date = format_date(start_date)
    formatted_end_date = format_date(end_date)

    # Generate animation using Matplotlib
    fig, ax = plt.subplots(figsize=(6, 10 * chart_height_pct))  # Adjustable chart height
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    ax.set_title(f'{ticker_type} Ticker: {ticker}', fontsize=16, color='white', pad=30)
    ax.set_xlabel('Date', color='white')
    ax.set_ylabel('Price', color='white')

    # Display start and end dates at the top
    if include_start_date:
        fig.text(0.5, 0.95, f"Start Date: {formatted_start_date}", ha='center', va='center', color='white', fontsize=12)
    if include_end_date:
        fig.text(0.5, 0.92, f"End Date: {formatted_end_date}", ha='center', va='center', color='white', fontsize=12)
    
    # Display custom text if provided
    if custom_text:
        fig.text(0.5, 0.89, custom_text, ha='center', va='center', color='white', fontsize=12)

    # Display watermark if provided
    if watermark_text:
        fig.text(0.5, 0.5, watermark_text, ha='center', va='center', color=watermark_color, fontsize=40, alpha=0.5)

    # Create a progress bar
    progress_bar = tqdm(total=len(data), desc="Generating Animation", unit="frames")

    def update(frame):
        ax.clear()
        ax.plot(data.index[:frame], data['Close'][:frame], color='green')
        ax.set_title(f'{ticker_type} Ticker: {ticker}', fontsize=16, color='white', pad=30)
        ax.set_xlabel('Date', color='white')
        ax.set_ylabel('Price', color='white')

        # Display the current stock price next to the line
        current_price = data['Close'][frame]
        ax.text(data.index[frame], current_price, f"${current_price:.2f}", fontsize=14, ha='right', va='center', 
                bbox=dict(facecolor='yellow', edgecolor='white', boxstyle='round,pad=0.5'), color='black', fontweight='bold')

        # Set the x-axis date format and y-axis tick interval
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=x_ticks_interval))  # Configurable date interval
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.yaxis.set_major_locator(plt.MultipleLocator(y_ticks_interval))  # Configurable y-axis interval
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')

        progress_bar.update(1)  # Update the progress bar

    ani = FuncAnimation(fig, update, frames=len(data), repeat=False)

    # Construct the correct filename prefix based on the ticker type
    filename_prefix = f"mattyjacks-{ticker_type.lower()}-{ticker}_{start_date}_{end_date}.mp4"
    ani.save(filename_prefix, writer='ffmpeg', fps=30)

    # Close the progress bar
    progress_bar.close()

    # Update the UI
    status_label.config(text=f"Animation saved successfully as {filename_prefix}!")

# Set up the tkinter GUI
root = tk.Tk()
root.title("Ticker Animation Generator")

# Calculate default dates
default_end_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
default_start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')

# Ticker type radio buttons
ticker_type_var = tk.StringVar(value="Stock")
stock_radio = ttk.Radiobutton(root, text="Stock Ticker", variable=ticker_type_var, value="Stock")
crypto_radio = ttk.Radiobutton(root, text="Crypto Ticker", variable=ticker_type_var, value="Crypto")
stock_radio.grid(row=0, column=0, padx=10, pady=10)
crypto_radio.grid(row=0, column=1, padx=10, pady=10)

# Ticker entry
ticker_label = ttk.Label(root, text="Ticker Symbol:")
ticker_label.grid(row=1, column=0, padx=10, pady=10)
ticker_entry = ttk.Entry(root)
ticker_entry.grid(row=1, column=1, padx=10, pady=10)

# Start date entry with default value
start_label = ttk.Label(root, text="Start Date (YYYY-MM-DD):")
start_label.grid(row=2, column=0, padx=10, pady=10)
start_entry = ttk.Entry(root)
start_entry.insert(0, default_start_date)  # Set default start date
start_entry.grid(row=2, column=1, padx=10, pady=10)

# End date entry with default value
end_label = ttk.Label(root, text="End Date (YYYY-MM-DD):")
end_label.grid(row=3, column=0, padx=10, pady=10)
end_entry = ttk.Entry(root)
end_entry.insert(0, default_end_date)  # Set default end date
end_entry.grid(row=3, column=1, padx=10, pady=10)

# Skip Days entry
skip_days_label = ttk.Label(root, text="Skip Days:")
skip_days_label.grid(row=4, column=0, padx=10, pady=10)
skip_days_entry = ttk.Entry(root)
skip_days_entry.insert(0, "0")  # Default value
skip_days_entry.grid(row=4, column=1, padx=10, pady=10)

# Include Start Date checkbox
include_start_var = tk.BooleanVar()
include_start_check = ttk.Checkbutton(root, text="Include Start Date", variable=include_start_var)
include_start_check.grid(row=5, column=0, columnspan=2, pady=5)

# Include End Date checkbox
include_end_var = tk.BooleanVar()
include_end_check = ttk.Checkbutton(root, text="Include End Date", variable=include_end_var)
include_end_check.grid(row=6, column=0, columnspan=2, pady=5)

# Custom Text checkbox and text area
custom_text_var = tk.BooleanVar()
custom_text_check = ttk.Checkbutton(root, text="Include Custom Text", variable=custom_text_var)
custom_text_check.grid(row=7, column=0, columnspan=2, pady=5)
custom_text_box = Text(root, height=4, width=30)
custom_text_box.grid(row=8, column=0, columnspan=2, padx=10, pady=5)

# X-axis ticks interval
x_ticks_label = ttk.Label(root, text="X-axis Ticks Interval:")
x_ticks_label.grid(row=9, column=0, padx=10, pady=10)
x_ticks_entry = ttk.Entry(root)
x_ticks_entry.insert(0, "1")  # Default value for month intervals
x_ticks_entry.grid(row=9, column=1, padx=10, pady=10)

# Y-axis ticks interval
y_ticks_label = ttk.Label(root, text="Y-axis Ticks Interval:")
y_ticks_label.grid(row=10, column=0, padx=10, pady=10)
y_ticks_entry = ttk.Entry(root)
y_ticks_entry.insert(0, "10")  # Default value
y_ticks_entry.grid(row=10, column=1, padx=10, pady=10)

# Chart height percentage
chart_height_label = ttk.Label(root, text="Chart Height Percentage:")
chart_height_label.grid(row=11, column=0, padx=10, pady=10)
chart_height_entry = ttk.Entry(root)
chart_height_entry.insert(0, "100")  # Default value
chart_height_entry.grid(row=11, column=1, padx=10, pady=10)

# Watermark text entry
watermark_label = ttk.Label(root, text="Watermark Text:")
watermark_label.grid(row=12, column=0, padx=10, pady=10)
watermark_entry = ttk.Entry(root)
watermark_entry.grid(row=12, column=1, padx=10, pady=10)

# Watermark color entry
watermark_color_label = ttk.Label(root, text="Watermark Color:")
watermark_color_label.grid(row=13, column=0, padx=10, pady=10)
watermark_color_entry = ttk.Entry(root)
watermark_color_entry.insert(0, "white")  # Default color
watermark_color_entry.grid(row=13, column=1, padx=10, pady=10)

# Cut Initial Frames checkbox
cut_initial_frames_var = tk.BooleanVar()
cut_initial_frames_check = ttk.Checkbutton(root, text="Cut Initial 10% Frames", variable=cut_initial_frames_var)
cut_initial_frames_check.grid(row=14, column=0, columnspan=2, pady=5)

# Generate button
generate_button = ttk.Button(root, text="Generate Animation", command=generate_animation)
generate_button.grid(row=15, column=0, columnspan=2, pady=20)

# Status label to show messages
status_label = ttk.Label(root, text="")
status_label.grid(row=16, column=0, columnspan=2, pady=10)

root.mainloop()

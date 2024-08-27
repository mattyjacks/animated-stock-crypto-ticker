import tkinter as tk
from tkinter import ttk
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

# Function to generate the animation
def generate_animation():
    ticker = ticker_entry.get()
    start_date = start_entry.get()
    end_date = end_entry.get()
    
    # Fetch stock data
    data = yf.download(ticker, start=start_date, end=end_date)
    
    # Generate animation using Matplotlib
    fig, ax = plt.subplots(figsize=(6, 10))  # Vertical 1080p format
    ax.set_title(f'Stock Ticker: {ticker}')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    
    # Create a progress bar
    progress_bar = tqdm(total=len(data), desc="Generating Animation", unit="frames")

    def update(frame):
        ax.clear()
        ax.plot(data.index[:frame], data['Close'][:frame], color='blue')
        ax.set_title(f'Stock Ticker: {ticker}')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        progress_bar.update(1)  # Update the progress bar

    ani = FuncAnimation(fig, update, frames=len(data), repeat=False)
    
    # Save the animation as an MP4
    ani.save(f'{ticker}_animation.mp4', writer='ffmpeg', fps=30)

    # Close the progress bar
    progress_bar.close()

    # Update the UI
    status_label.config(text="Animation saved successfully!")

# Set up the tkinter GUI
root = tk.Tk()
root.title("Stock Ticker Animation Generator")

# Calculate default dates
default_end_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
default_start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')

# Ticker entry
ticker_label = ttk.Label(root, text="Stock Ticker:")
ticker_label.grid(row=0, column=0, padx=10, pady=10)
ticker_entry = ttk.Entry(root)
ticker_entry.grid(row=0, column=1, padx=10, pady=10)

# Start date entry with default value
start_label = ttk.Label(root, text="Start Date (YYYY-MM-DD):")
start_label.grid(row=1, column=0, padx=10, pady=10)
start_entry = ttk.Entry(root)
start_entry.insert(0, default_start_date)  # Set default start date
start_entry.grid(row=1, column=1, padx=10, pady=10)

# End date entry with default value
end_label = ttk.Label(root, text="End Date (YYYY-MM-DD):")
end_label.grid(row=2, column=0, padx=10, pady=10)
end_entry = ttk.Entry(root)
end_entry.insert(0, default_end_date)  # Set default end date
end_entry.grid(row=2, column=1, padx=10, pady=10)

# Generate button
generate_button = ttk.Button(root, text="Generate Animation", command=generate_animation)
generate_button.grid(row=3, column=0, columnspan=2, pady=20)

# Status label
status_label = ttk.Label(root, text="")
status_label.grid(row=4, column=0, columnspan=2, pady=10)

root.mainloop()

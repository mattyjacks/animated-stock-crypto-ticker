import os
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from matplotlib.animation import FuncAnimation
from tkinter import Tk, ttk, StringVar, IntVar, Text, OptionMenu
from datetime import datetime, timedelta
import matplotlib.patches as patches
from PIL import ImageFont, ImageDraw, Image

# Function to determine ordinal suffix
def ordinal_suffix(day):
    return "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

# Generate animation
def generate_animation():
    status_label.config(text="Fetching data...")

    ticker = ticker_entry.get().upper()
    start_date = start_entry.get()
    end_date = end_entry.get()
    skip_days = int(skip_days_entry.get()) if skip_days_entry.get() else 0
    custom_text = custom_text_entry.get("1.0", "end-1c")
    y_tick_interval = int(y_ticks_entry.get()) if y_ticks_entry.get() else 10
    chart_height_percentage = int(chart_height_entry.get()) if chart_height_entry.get() else 100
    watermark_text = watermark_entry.get("1.0", "end-1c")
    watermark_color = watermark_color_entry.get() or "#FFFFFF"
    cut_out_frames = cut_out_frames_var.get()
    include_start_date = include_start_var.get()
    include_end_date = include_end_var.get()

    if ticker_type.get() == "crypto":
        # Crypto data fetching (using yfinance with crypto symbol)
        ticker = ticker + "-USD"
        data = yf.download(ticker, start=start_date, end=end_date, interval='1d')
    else:
        # Stock data fetching
        data = yf.download(ticker, start=start_date, end=end_date, interval='1d')

    fig, ax = plt.subplots()
    ax.set_facecolor('black')
    fig.patch.set_facecolor('black')

    def update(frame):
        ax.clear()
        ax.set_facecolor('black')
        fig.patch.set_facecolor('black')
        plt.xticks(color='white')
        plt.yticks(color='white')
        plt.grid(True, color='gray')
        plt.xlabel('Date', color='white')
        plt.ylabel('Price', color='white')

        ax.plot(data.index[:frame + 1], data['Close'][:frame + 1], color='green')

        # Add the running price label
        last_price = data['Close'][frame]
        ax.text(data.index[frame], last_price, f"${last_price:.2f}", fontsize=14,
                bbox=dict(facecolor='yellow', alpha=0.7, edgecolor='white', boxstyle='round,pad=0.5'))

        # Add watermark
        ax.text(0.5, 0.5, watermark_text, color=watermark_color, fontsize=24, alpha=0.5, ha='center', va='center', transform=ax.transAxes, fontweight='bold')

        # Add custom text, start date, and end date
        if include_start_date:
            ax.text(0.5, 1.05, f"Start Date: {datetime.strptime(start_date, '%Y-%m-%d').strftime('%B')} {int(datetime.strptime(start_date, '%Y-%m-%d').strftime('%d'))}{ordinal_suffix(int(datetime.strptime(start_date, '%Y-%m-%d').strftime('%d')))} {datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y')}",
                    color='white', fontsize=10, ha='center', transform=ax.transAxes)
        if include_end_date:
            ax.text(0.5, 1.02, f"End Date: {datetime.strptime(end_date, '%Y-%m-%d').strftime('%B')} {int(datetime.strptime(end_date, '%Y-%m-%d').strftime('%d'))}{ordinal_suffix(int(datetime.strptime(end_date, '%Y-%m-%d').strftime('%d')))} {datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y')}",
                    color='white', fontsize=10, ha='center', transform=ax.transAxes)
        if custom_text:
            ax.text(0.5, 0.98, custom_text, color='white', fontsize=10, ha='center', transform=ax.transAxes)

        # Set limits and aspect ratio
        ax.set_ylim(data['Close'].min() * 0.95, data['Close'].max() * 1.05)
        ax.set_xlim(data.index[0], data.index[-1])

        # Set the tick interval and formatting for x-axis
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

    ani = FuncAnimation(fig, update, frames=len(data), repeat=False)

    # Define output file name
    start_str = datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y-%m-%d')
    end_str = datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y-%m-%d')
    filename = f"{ticker_type}-anim_{ticker.replace('-USD', '')}_{start_str}_{end_str}.mp4"

    status_label.config(text="Generating animation...")

    ani.save(filename, writer='ffmpeg', fps=30, dpi=200)

    # Cut out initial frames if specified
    if cut_out_frames:
        os.system(f"ffmpeg -i {filename} -vf 'select=gt(n\,{len(data) * 0.1})' -vsync vfr output_{filename}")

    status_label.config(text=f"Animation saved as {filename}")

# Set up the tkinter interface
root = Tk()
root.title("Stock/Crypto Ticker Animation Generator")

ticker_type = StringVar(value="stock")
ticker_var = StringVar()
start_date_var = StringVar()
end_date_var = StringVar()
custom_text_var = StringVar()
watermark_color_var = StringVar()

# Ticker type selection (Radio buttons)
ticker_type_label = ttk.Label(root, text="Select Ticker Type:")
ticker_type_label.grid(row=0, column=0, padx=10, pady=10)
stock_radio = ttk.Radiobutton(root, text="Stock Ticker", variable=ticker_type, value="stock")
crypto_radio = ttk.Radiobutton(root, text="Crypto Ticker", variable=ticker_type, value="crypto")
stock_radio.grid(row=0, column=1, padx=10, pady=10)
crypto_radio.grid(row=0, column=2, padx=10, pady=10)

# Ticker entry
ticker_label = ttk.Label(root, text="Ticker Symbol:")
ticker_label.grid(row=1, column=0, padx=10, pady=10)
ticker_entry = ttk.Entry(root)
ticker_entry.grid(row=1, column=1, padx=10, pady=10)

# Date entries
start_label = ttk.Label(root, text="Start Date (YYYY-MM-DD):")
start_label.grid(row=2, column=0, padx=10, pady=10)
start_entry = ttk.Entry(root)
start_entry.insert(0, (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'))  # Default start date
start_entry.grid(row=2, column=1, padx=10, pady=10)

end_label = ttk.Label(root, text="End Date (YYYY-MM-DD):")
end_label.grid(row=3, column=0, padx=10, pady=10)
end_entry = ttk.Entry(root)
end_entry.insert(0, (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'))  # Default end date
end_entry.grid(row=3, column=1, padx=10, pady=10)

# Custom text at the top
custom_text_label = ttk.Label(root, text="Custom Text at Top:")
custom_text_label.grid(row=4, column=0, padx=10, pady=10)
custom_text_entry = Text(root, height=4, width=30)
custom_text_entry.grid(row=4, column=1, padx=10, pady=10)

# Watermark text and color
watermark_label = ttk.Label(root, text="Watermark Text:")
watermark_label.grid(row=5, column=0, padx=10, pady=10)
watermark_entry = Text(root, height=2, width=30)
watermark_entry.grid(row=5, column=1, padx=10, pady=10)

watermark_color_label = ttk.Label(root, text="Watermark Color (hex):")
watermark_color_label.grid(row=6, column=0, padx=10, pady=10)
watermark_color_entry = ttk.Entry(root)
watermark_color_entry.grid(row=6, column=1, padx=10, pady=10)

# Include Start Date and End Date
include_start_var = IntVar(value=1)
include_start_checkbox = ttk.Checkbutton(root, text="Include Start Date", variable=include_start_var)
include_start_checkbox.grid(row=7, column=0, padx=10, pady=10)

include_end_var = IntVar(value=1)
include_end_checkbox = ttk.Checkbutton(root, text="Include End Date", variable=include_end_var)
include_end_checkbox.grid(row=7, column=1, padx=10, pady=10)

# Cut out initial frames option
cut_out_frames_var = IntVar(value=0)
cut_out_frames_checkbox = ttk.Checkbutton(root, text="Cut Out InitialFrames", variable=cut_out_frames_var)
cut_out_frames_checkbox.grid(row=8, column=0, padx=10, pady=10)

# Skip days option
skip_days_label = ttk.Label(root, text="Skip Days:")
skip_days_label.grid(row=9, column=0, padx=10, pady=10)
skip_days_entry = ttk.Entry(root)
skip_days_entry.insert(0, "0")  # Default skip days
skip_days_entry.grid(row=9, column=1, padx=10, pady=10)

# Y-axis ticks interval
y_ticks_label = ttk.Label(root, text="Y-axis Tick Interval:")
y_ticks_label.grid(row=10, column=0, padx=10, pady=10)
y_ticks_entry = ttk.Entry(root)
y_ticks_entry.grid(row=10, column=1, padx=10, pady=10)

# Chart height percentage
chart_height_label = ttk.Label(root, text="Chart Height Percentage:")
chart_height_label.grid(row=11, column=0, padx=10, pady=10)
chart_height_entry = ttk.Entry(root)
chart_height_entry.insert(0, "100")  # Default chart height percentage
chart_height_entry.grid(row=11, column=1, padx=10, pady=10)

# Generate button
generate_button = ttk.Button(root, text="Generate Animation", command=generate_animation)
generate_button.grid(row=12, column=0, columnspan=2, padx=10, pady=20)

# Status label
status_label = ttk.Label(root, text="")
status_label.grid(row=13, column=0, columnspan=2, padx=10, pady=10)

# Start the main loop
root.mainloop()


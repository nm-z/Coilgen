import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import shapely.geometry as sg
import ezdxf
import svgwrite
import logging
import math
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to generate coil geometry
def generate_coil(turns, width, spacing, shape='spiral'):
    logging.info(f'Starting coil generation with turns={turns}, width={width}, spacing={spacing}, shape={shape}')
    if turns <= 0 or width <= 0 or spacing < 0:
        logging.error(f'Invalid parameters: turns={turns}, width={width}, spacing={spacing}')
        raise ValueError("Invalid parameters for coil generation")
    
    points = []
    baseX, baseY = 0, 0  # Center of the coil
    
    if shape == 'spiral':
        radius = width  # Starting radius
        sides = 100  # Number of sides to approximate a circle
        segangle = 360 / sides
        segradius = spacing / sides

        for i in range(turns * sides):
            startX = baseX + (radius + segradius * i) * math.cos(math.radians(segangle * i))
            startY = baseY + (radius + segradius * i) * math.sin(math.radians(segangle * i))
            points.append((startX, startY))
    elif shape == 'square':
        side_length = width
        for turn in range(turns):
            points.extend([
                (baseX + side_length/2 + turn*spacing, baseY + side_length/2 + turn*spacing),
                (baseX - side_length/2 - turn*spacing, baseY + side_length/2 + turn*spacing),
                (baseX - side_length/2 - turn*spacing, baseY - side_length/2 - turn*spacing),
                (baseX + side_length/2 + turn*spacing, baseY - side_length/2 - turn*spacing),
            ])
    
    coil = sg.LineString(points)
    logging.info(f'Generated {shape} coil with {len(points)} points')
    return coil

# Function to update coil visualization
def update_coil():
    try:
        turns = int(turns_var.get())
        width = float(width_var.get())
        spacing = float(spacing_var.get())
        shape = shape_var.get()
        logging.info(f'Updating coil with turns={turns}, width={width}, spacing={spacing}, shape={shape}')
        if turns <= 0 or width <= 0 or spacing < 0:
            logging.error(f'Invalid input values: turns={turns}, width={width}, spacing={spacing}')
            raise ValueError("Invalid input values")

        coil = generate_coil(turns, width, spacing, shape)

        ax.clear()
        x, y = coil.xy
        ax.plot(x, y)
        canvas.draw()
        logging.info('Coil visualization updated')
    except ValueError as e:
        logging.exception('Error updating coil')
        messagebox.showerror("Invalid input", str(e))

# Function to export coil to different formats
def export_coil():
    try:
        turns = int(turns_var.get() or '0')
        width = float(width_var.get() or '0')
        spacing = float(spacing_var.get() or '0')
        shape = shape_var.get()
        logging.info(f'Exporting coil with turns={turns}, width={width}, spacing={spacing}, shape={shape}')
        if turns <= 0 or width <= 0 or spacing < 0:
            logging.error(f'Invalid input values: turns={turns}, width={width}, spacing={spacing}')
            raise ValueError("Invalid input values")

        coil = generate_coil(turns, width, spacing, shape)
        x, y = coil.xy

        default_filename = f"coil_{shape}_{turns}turns_{width}width_{spacing}spacing"

        file_types = [('Gerber Files', '*.gbr'), ('DXF Files', '*.dxf'), ('SVG Files', '*.svg'), ('Drill Files', '*.txt')]
        file_path = filedialog.asksaveasfilename(
            initialdir="/home/nate/Coilgen/Coilgen/Generated_Coils",
            initialfile=default_filename,
            filetypes=file_types,
            defaultextension=file_types
        )

        if not file_path:
            logging.info('Export cancelled by user')
            return

        logging.info(f'Exporting coil to {file_path}')
        if file_path.endswith('.gbr'):
            logging.info('Writing Gerber file')
            with open(file_path, 'w') as f:
                f.write('%FSLAX25Y25*%\nG04 EAGLE Gerber RS-274X export*\n%MOIN*%\n')
                f.write('%ADD10C,{:.4f}*%\n'.format(width))
                for xi, yi in zip(x, y):
                    f.write('X{:.4f}Y{:.4f}D01*\n'.format(xi, yi))
                f.write('M02*\n')
            logging.info(f'Coil exported to Gerber file: {file_path}')
        elif file_path.endswith('.dxf'):
            logging.info('Creating DXF document')
            doc = ezdxf.new(dxfversion='R2010')
            msp = doc.modelspace()
            msp.add_lwpolyline(list(zip(x, y)))
            doc.saveas(file_path)
            logging.info(f'Coil exported to DXF file: {file_path}')
        elif file_path.endswith('.svg'):
            logging.info('Creating SVG document')
            dwg = svgwrite.Drawing(file_path, profile='tiny')
            dwg.add(dwg.polyline(list(zip(x, y)), stroke=svgwrite.rgb(10, 10, 16, '%')))
            dwg.save()
            logging.info(f'Coil exported to SVG file: {file_path}')
        elif file_path.endswith('.txt'):
            logging.info('Writing Drill file')
            with open(file_path, 'w') as f:
                for xi, yi in zip(x, y):
                    f.write('{:.4f}, {:.4f}\n'.format(xi, yi))
            logging.info(f'Coil exported to Drill file: {file_path}')
        logging.info('Export process completed successfully')
    except ValueError as e:
        logging.exception('Error exporting coil')
        messagebox.showerror("Invalid input", str(e))

# GUI Setup
logging.info('Starting PCB Coil Designer GUI setup')
root = tk.Tk()
root.title("PCB Coil Designer")

turns_label = tk.Label(root, text="Turns:")
turns_label.grid(row=0, column=0)
turns_var = tk.StringVar(value='5')
turns_entry = tk.Entry(root, textvariable=turns_var)
turns_entry.grid(row=0, column=1)

width_label = tk.Label(root, text="Width:")
width_label.grid(row=1, column=0)
width_var = tk.StringVar(value='1.0')
width_entry = tk.Entry(root, textvariable=width_var)
width_entry.grid(row=1, column=1)

spacing_label = tk.Label(root, text="Spacing:")
spacing_label.grid(row=2, column=0)
spacing_var = tk.StringVar(value='0.2')
spacing_entry = tk.Entry(root, textvariable=spacing_var)
spacing_entry.grid(row=2, column=1)

shape_label = tk.Label(root, text="Shape:")
shape_label.grid(row=3, column=0)
shape_var = tk.StringVar(value='spiral')
shape_menu = tk.OptionMenu(root, shape_var, 'spiral', 'square')
shape_menu.grid(row=3, column=1)

fig, ax = plt.subplots(figsize=(5, 5))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=4, columnspan=2)

generate_button = tk.Button(root, text="Generate Coil", command=update_coil)
generate_button.grid(row=5, column=0)

export_button = tk.Button(root, text="Export", command=export_coil)
export_button.grid(row=5, column=1)

logging.info('PCB Coil Designer GUI setup complete')
root.mainloop()
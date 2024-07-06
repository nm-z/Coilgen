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
def generate_coil(turns, width, spacing, inner_diameter, outer_diameter, shape='spiral'):
    logging.info(f'Starting coil generation with turns={turns}, width={width}, spacing={spacing}, shape={shape}, inner_diameter={inner_diameter}, outer_diameter={outer_diameter}')
    if turns <= 0 or width <= 0 or spacing < 0 or inner_diameter <= 0 or outer_diameter <= 0 or outer_diameter <= inner_diameter:
        logging.error(f'Invalid parameters: turns={turns}, width={width}, spacing={spacing}, inner_diameter={inner_diameter}, outer_diameter={outer_diameter}')
        raise ValueError("Invalid parameters for coil generation")
    
    points = []
    baseX, baseY = 0, 0  # Center of the coil
    
    if shape == 'spiral':
        radius = inner_diameter / 2.0  # Starting radius
        final_radius = outer_diameter / 2.0
        total_sides = int(turns * 100)  # Number of sides to approximate a circle
        delta_radius = (final_radius - radius) / total_sides
        segangle = 360 / 100

        for i in range(total_sides):
            startX = baseX + (radius + delta_radius * i) * math.cos(math.radians(segangle * i))
            startY = baseY + (radius + delta_radius * i) * math.sin(math.radians(segangle * i))
            points.append((startX, startY))
    elif shape == 'square':
        side_length = inner_diameter
        step = (outer_diameter - inner_diameter) / (4 * turns)
        for turn in range(turns):
            points.extend([
                (baseX + side_length/2 + turn*step, baseY + side_length/2 + turn*step),
                (baseX - side_length/2 - turn*step, baseY + side_length/2 + turn*step),
                (baseX - side_length/2 - turn*step, baseY - side_length/2 - turn*step),
                (baseX + side_length/2 + turn*step, baseY - side_length/2 - turn*step),
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
        inner_diameter = float(inner_d_var.get())
        outer_diameter = float(outer_d_var.get())
        shape = shape_var.get()
        logging.info(f'Updating coil with turns={turns}, width={width}, spacing={spacing}, shape={shape}, inner_diameter={inner_diameter}, outer_diameter={outer_diameter}')
        if turns <= 0 or width <= 0 or spacing < 0 or inner_diameter <= 0 or outer_diameter <= 0 or outer_diameter <= inner_diameter:
            logging.error(f'Invalid input values: turns={turns}, width={width}, spacing={spacing}, inner_diameter={inner_diameter}, outer_diameter={outer_diameter}')
            raise ValueError("Invalid input values")

        coil = generate_coil(turns, width, spacing, inner_diameter, outer_diameter, shape)

        ax.clear()
        x, y = coil.xy
        ax.plot(x, y, color='blue')
        ax.set_facecolor('black')
        ax.set_aspect('equal', adjustable='box')
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda val, pos: f'{val*25.4:.0f} mm'))
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, pos: f'{val*25.4:.0f} mm'))
        canvas.draw()
        logging.info('Coil visualization updated')
    except ValueError as e:
        logging.exception('Error updating coil')
        messagebox.showerror("Invalid input", str(e))

# Function to export coil to different formats
def export_coil():
    try:
        turns = int(turns_var.get())
        width = float(width_var.get())
        spacing = float(spacing_var.get())
        inner_diameter = float(inner_d_var.get())
        outer_diameter = float(outer_d_var.get())
        shape = shape_var.get()
        logging.info(f'Exporting coil with turns={turns}, width={width}, spacing={spacing}, shape={shape}, inner_diameter={inner_diameter}, outer_diameter={outer_diameter}')
        if turns <= 0 or width <= 0 or spacing < 0 or inner_diameter <= 0 or outer_diameter <= 0 or outer_diameter <= inner_diameter:
            logging.error(f'Invalid input values: turns={turns}, width={width}, spacing={spacing}, inner_diameter={inner_diameter}, outer_diameter={outer_diameter}')
            raise ValueError("Invalid input values")

        coil = generate_coil(turns, width, spacing, inner_diameter, outer_diameter, shape)
        x, y = coil.xy

        default_filename = f"coil_{shape}_{turns}turns_{width}width_{spacing}spacing_{inner_diameter}inner_{outer_diameter}outer"

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
root.configure(bg='black')

root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

mainframe = tk.Frame(root, bg='black')
mainframe.grid(row=0, column=0, sticky='nsew')
mainframe.rowconfigure(4, weight=1)
mainframe.columnconfigure(1, weight=1)

turns_label = tk.Label(mainframe, text="Turns:", bg='black', fg='white')
turns_label.grid(row=0, column=0, sticky='e')
turns_var = tk.StringVar(value='5')
turns_entry = tk.Entry(mainframe, textvariable=turns_var)
turns_entry.grid(row=0, column=1, sticky='ew')

width_label = tk.Label(mainframe, text="Width:", bg='black', fg='white')
width_label.grid(row=1, column=0, sticky='e')
width_var = tk.StringVar(value='1.0')
width_entry = tk.Entry(mainframe, textvariable=width_var)
width_entry.grid(row=1, column=1, sticky='ew')

spacing_label = tk.Label(mainframe, text="Spacing:", bg='black', fg='white')
spacing_label.grid(row=2, column=0, sticky='e')
spacing_var = tk.StringVar(value='0.2')
spacing_entry = tk.Entry(mainframe, textvariable=spacing_var)
spacing_entry.grid(row=2, column=1, sticky='ew')

inner_d_label = tk.Label(mainframe, text="Inner Diameter:", bg='black', fg='white')
inner_d_label.grid(row=3, column=0, sticky='e')
inner_d_var = tk.StringVar(value='1.0')
inner_d_entry = tk.Entry(mainframe, textvariable=inner_d_var)
inner_d_entry.grid(row=3, column=1, sticky='ew')

outer_d_label = tk.Label(mainframe, text="Outer Diameter:", bg='black', fg='white')
outer_d_label.grid(row=4, column=0, sticky='e')
outer_d_var = tk.StringVar(value='10.0')
outer_d_entry = tk.Entry(mainframe, textvariable=outer_d_var)
outer_d_entry.grid(row=4, column=1, sticky='ew')

shape_label = tk.Label(mainframe, text="Shape:", bg='black', fg='white')
shape_label.grid(row=5, column=0, sticky='e')
shape_var = tk.StringVar(value='spiral')
shape_menu = tk.OptionMenu(mainframe, shape_var, 'spiral', 'square')
shape_menu.grid(row=5, column=1, sticky='ew')

fig, ax = plt.subplots(figsize=(5, 5))
ax.set_facecolor('black')
fig.patch.set_facecolor('black')
canvas = FigureCanvasTkAgg(fig, master=mainframe)
canvas.get_tk_widget().grid(row=6, columnspan=2, sticky='nsew')

generate_button = tk.Button(mainframe, text="Generate Coil", command=update_coil, bg='black', fg='white')
generate_button.grid(row=7, column=0, sticky='ew')

export_button = tk.Button(mainframe, text="Export", command=export_coil, bg='black', fg='white')
export_button.grid(row=7, column=1, sticky='ew')

logging.info('PCB Coil Designer GUI setup complete')
root.mainloop()

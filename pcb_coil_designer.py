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
POINTS = 1.0  # Adjust this value as needed for proper scaling

# Function to generate coil geometry
def generate_coil(turns, width, spacing, inner_diameter, outer_diameter, shape='spiral'):
    logging.info(f'Starting coil generation with turns={turns}, width={width}, spacing={spacing}, shape={shape}, inner_diameter={inner_diameter}, outer_diameter={outer_diameter}')
    if turns <= 0 or width <= 0 or spacing < 0 or inner_diameter <= 0 or outer_diameter <= 0 or outer_diameter <= inner_diameter:
        logging.error(f'Invalid parameters: turns={turns}, width={width}, spacing={spacing}, inner_diameter={inner_diameter}, outer_diameter={outer_diameter}')
        raise ValueError("Invalid parameters for coil generation")
    
    points = []
    baseX, baseY = 0, 0  # Center of the coil
    
    if shape == 'spiral':
        radius = inner_diameter / 2.0
        final_radius = outer_diameter / 2.0
        total_sides = int(turns * 100)
        delta_radius = (final_radius - radius) / total_sides
        segangle = 360 / 100

        for i in range(total_sides):
            angle = math.radians(segangle * i)
            r = radius + delta_radius * i
            startX = baseX + r * math.cos(angle)
            startY = baseY + r * math.sin(angle)
            points.append((startX, startY))
    elif shape == 'square':
        side_length = inner_diameter
        step = (outer_diameter - inner_diameter) / (4 * turns)
        for turn in range(turns):
            current_side = side_length + 2 * turn * step
            half_side = current_side / 2
            points.extend([
                (baseX + half_side, baseY + half_side),
                (baseX - half_side, baseY + half_side),
                (baseX - half_side, baseY - half_side),
                (baseX + half_side, baseY - half_side),
            ])
        points.append(points[0])  # Close the square
    
    coil = sg.LineString(points)
    logging.info(f'Generated {shape} coil with {len(points)} points')
    return coil

# Function to update coil visualization
def update_plot_settings(ax):
    ax.set_facecolor('black')
    ax.grid(True, color='gray', linestyle='--', linewidth=0.5, zorder=0)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0f} mm'))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0f} mm'))
    ax.set_xlabel('mm')
    ax.set_ylabel('mm')

def update_coil():
    try:
        # Get parameters
        turns = int(turns_var.get())
        width = float(width_var.get())
        spacing = float(spacing_var.get())
        inner_diameter = float(inner_diameter_var.get())
        outer_diameter = float(outer_diameter_var.get())
        shape = shape_var.get()

        # Validate parameters
        if turns <= 0 or width <= 0 or spacing < 0 or inner_diameter < 0 or outer_diameter <= inner_diameter:
            raise ValueError("Invalid input values")

        logging.info(f'Updating coil with turns={turns}, width={width}, spacing={spacing}, '
                     f'inner_diameter={inner_diameter}, outer_diameter={outer_diameter}, shape={shape}')

        # Generate coil
        coil = generate_coil(turns, width, spacing, shape, inner_diameter, outer_diameter)

        # Update plot
        ax.clear()
        update_plot_settings(ax)
        ax.plot(*coil.xy, color='blue', linewidth=width*POINTS, zorder=2)        
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
        inner_diameter = float(inner_diameter_var.get())
        outer_diameter = float(outer_diameter_var.get())
        shape = shape_var.get()

        logging.info(f'Exporting coil with turns={turns}, width={width}, spacing={spacing}, '
                     f'inner_diameter={inner_diameter}, outer_diameter={outer_diameter}, shape={shape}')

        if turns <= 0 or width <= 0 or spacing < 0 or inner_diameter < 0 or outer_diameter <= inner_diameter:
            raise ValueError("Invalid input values")

        coil = generate_coil(turns, width, spacing, shape, inner_diameter, outer_diameter)
        x, y = coil.xy
        
        logging.info(f'Generated coil with {len(x)} points')

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

        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

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
    except Exception as e:
        logging.exception('Error exporting coil')
        messagebox.showerror("Export Error", str(e))

# GUI Setup
logging.info('Starting PCB Coil Designer GUI setup')
root = tk.Tk()
root.title("PCB Coil Designer")
root.configure(bg='black')
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.rowconfigure(6, weight=1)

turns_label = tk.Label(root, text="Turns:", bg='black', fg='white')
turns_label.grid(row=0, column=0, sticky='e')
turns_var = tk.StringVar(value='5')
turns_entry = tk.Entry(root, textvariable=turns_var)
turns_entry.grid(row=0, column=1, sticky='w')

width_label = tk.Label(root, text="Width:", bg='black', fg='white')
width_label.grid(row=1, column=0, sticky='e')
width_var = tk.StringVar(value='1.0')
width_entry = tk.Entry(root, textvariable=width_var)
width_entry.grid(row=1, column=1, sticky='w')

spacing_label = tk.Label(root, text="Spacing:", bg='black', fg='white')
spacing_label.grid(row=2, column=0, sticky='e')
spacing_var = tk.StringVar(value='0.2')
spacing_entry = tk.Entry(root, textvariable=spacing_var)
spacing_entry.grid(row=2, column=1, sticky='w')

inner_diameter_label = tk.Label(root, text="Inner Diameter:", bg='black', fg='white')
inner_diameter_label.grid(row=3, column=0, sticky='e')
inner_diameter_var = tk.StringVar(value='10')
inner_diameter_entry = tk.Entry(root, textvariable=inner_diameter_var)
inner_diameter_entry.grid(row=3, column=1, sticky='w')

outer_diameter_label = tk.Label(root, text="Outer Diameter:", bg='black', fg='white')
outer_diameter_label.grid(row=4, column=0, sticky='e')
outer_diameter_var = tk.StringVar(value='20')
outer_diameter_entry = tk.Entry(root, textvariable=outer_diameter_var)
outer_diameter_entry.grid(row=4, column=1, sticky='w')

shape_label = tk.Label(root, text="Shape:", bg='black', fg='white')
shape_label.grid(row=5, column=0, sticky='e')
shape_var = tk.StringVar(value='spiral')
shape_menu = tk.OptionMenu(root, shape_var, 'spiral', 'square')
shape_menu.grid(row=5, column=1, sticky='w')

fig, ax = plt.subplots(figsize=(5, 5))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=6, columnspan=2, sticky='nsew')

generate_button = tk.Button(root, text="Generate Coil", command=update_coil)
generate_button.grid(row=7, column=0, sticky='ew')

export_button = tk.Button(root, text="Export", command=export_coil)
export_button.grid(row=7, column=1, sticky='ew')

logging.info('PCB Coil Designer GUI setup complete')
update_coil()
root.mainloop()

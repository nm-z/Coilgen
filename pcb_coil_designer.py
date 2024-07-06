import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import shapely.geometry as sg
from shapely.affinity import translate, rotate
import ezdxf
import svgwrite
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to generate coil geometry
def generate_coil(turns, width, spacing):
    logging.debug(f'Starting coil generation with turns={turns}, width={width}, spacing={spacing}')
    if turns <= 0 or width <= 0 or spacing < 0:
        logging.error(f'Invalid parameters: turns={turns}, width={width}, spacing={spacing}')
        raise ValueError("Invalid parameters for coil generation")
    
    points = [(0, 0)]
    x, y = 0, 0
    step = width + spacing
    for i in range(turns):
        x += step
        points.append((x, y))
        y += step
        points.append((x, y))
        x -= step
        points.append((x, y))
        y -= step
        points.append((x, y))
        step += width + spacing  # Increase the step for the next turn
    
    coil = sg.LineString(points)
    logging.debug(f'Generated coil with {len(points)} points')
    return coil


# Function to update coil visualization
def update_coil():
    try:
        turns = int(turns_var.get())
        width = float(width_var.get())
        spacing = float(spacing_var.get())
        logging.debug(f'Updating coil with turns={turns}, width={width}, spacing={spacing}')
        if turns <= 0 or width <= 0 or spacing < 0:
            logging.error(f'Invalid input values: turns={turns}, width={width}, spacing={spacing}')
            raise ValueError("Invalid input values")

        coil = generate_coil(turns, width, spacing)

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
        turns = int(turns_var.get())
        width = float(width_var.get())
        spacing = float(spacing_var.get())
        logging.debug(f'Exporting coil with turns={turns}, width={width}, spacing={spacing}')
        if turns <= 0 or width <= 0 or spacing < 0:
            logging.error(f'Invalid input values: turns={turns}, width={width}, spacing={spacing}')
            raise ValueError("Invalid input values")

        coil = generate_coil(turns, width, spacing)
        x, y = coil.xy

        default_filename = f"coil_{turns}turns_{width}width_{spacing}spacing"

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

        if file_path.endswith('.gbr'):
            with open(file_path, 'w') as f:
                f.write('%FSLAX25Y25*%\nG04 EAGLE Gerber RS-274X export*\n%MOIN*%\n')
                f.write('%ADD10C,{:.4f}*%\n'.format(width))
                for xi, yi in zip(x, y):
                    f.write('X{:.4f}Y{:.4f}D01*\n'.format(xi, yi))
                f.write('M02*\n')
            logging.info(f'Coil exported to Gerber file: {file_path}')
        elif file_path.endswith('.dxf'):
            doc = ezdxf.new(dxfversion='R2010')
            msp = doc.modelspace()
            msp.add_lwpolyline(list(zip(x, y)))
            doc.saveas(file_path)
            logging.info(f'Coil exported to DXF file: {file_path}')
        elif file_path.endswith('.svg'):
            dwg = svgwrite.Drawing(file_path, profile='tiny')
            dwg.add(dwg.polyline(list(zip(x, y)), stroke=svgwrite.rgb(10, 10, 16, '%')))
            dwg.save()
            logging.info(f'Coil exported to SVG file: {file_path}')
        elif file_path.endswith('.txt'):
            with open(file_path, 'w') as f:
                for xi, yi in zip(x, y):
                    f.write('{:.4f}, {:.4f}\n'.format(xi, yi))
            logging.info(f'Coil exported to Drill file: {file_path}')
    except ValueError as e:
        logging.exception('Error exporting coil')
        messagebox.showerror("Invalid input", str(e))

# GUI Setup
logging.info('Starting PCB Coil Designer GUI setup')
root = tk.Tk()
root.title("PCB Coil Designer")

mainframe = ttk.Frame(root, padding="10 10 10 10")
mainframe.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Input fields
ttk.Label(mainframe, text="Turns:").grid(row=0, column=0, sticky=tk.W)
turns_var = tk.StringVar(value='10')
turns_entry = ttk.Entry(mainframe, width=10, textvariable=turns_var)
turns_entry.grid(row=0, column=1)

ttk.Label(mainframe, text="Width:").grid(row=1, column=0, sticky=tk.W)
width_var = tk.StringVar(value='1.0')
width_entry = ttk.Entry(mainframe, width=10, textvariable=width_var)
width_entry.grid(row=1, column=1)

ttk.Label(mainframe, text="Spacing:").grid(row=2, column=0, sticky=tk.W)
spacing_var = tk.StringVar(value='0.2')
spacing_entry = ttk.Entry(mainframe, width=10, textvariable=spacing_var)
spacing_entry.grid(row=2, column=1)

# Visualization
fig, ax = plt.subplots(figsize=(5, 5))
canvas = FigureCanvasTkAgg(fig, master=mainframe)
canvas.get_tk_widget().grid(row=3, column=0, columnspan=2)

# Buttons
ttk.Button(mainframe, text="Generate Coil", command=update_coil).grid(row=4, column=0)
ttk.Button(mainframe, text="Export", command=export_coil).grid(row=4, column=1)

logging.info('PCB Coil Designer GUI setup complete')
root.mainloop()

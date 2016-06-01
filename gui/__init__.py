import Tkinter as tk
import ttk
import tkFileDialog
import tkMessageBox
from os import path
import PIL
from PIL import Image, ImageTk
from utils import resize as rz
from src import fingerprint
import glob

global_variables = {}

def init_screen():
    ipadding = 2

    #root window
    root = tk.Tk()
    global_variables['root_window'] = root
    root.resizable(0, 0)
    root.title("Fingerprint compression")

    ttk.Label(root, text="Image:").grid(row=0, column=0, padx=ipadding, pady=ipadding)
    ttk.Button(root, text="Browse", command=getfilename).grid(row=0, column=1, padx = ipadding, pady=ipadding, ipadx=ipadding, ipady=ipadding, sticky='EW')
    root.mainloop()


def getfilename():
    indir = "../" + path.dirname(path.realpath(__file__))
    v = tkFileDialog.askopenfile(initialdir=indir)
    if v:
        global_variables['img_path'] = v.name
        main_window()

def main_window():
    global_variables['root_window'].destroy()
    main_gui_window = tk.Tk()
    global_variables['main_window'] = main_gui_window
    main_gui_window.title(global_variables['img_path'])
    img = Image.open(global_variables['img_path'])
    global_variables['working_image'] = rz.resize(img)
    img = rz.resize(img)
    photo = ImageTk.PhotoImage(img)
    label = tk.Label(main_gui_window, image=photo)
    label.image = photo #IDEK why
    global_variables['image_label'] = label
    global_variables['gui_image'] = label.image
    label.grid(row = 0, column= 0, rowspan=12)

    # -- Menu -- #
    menu = tk.Menu(main_gui_window)
    main_gui_window.config(menu=menu)
    # -- Main Submenu -- #
    mainMenu = tk.Menu(menu)
    mainMenu.add_command(label="Open file", command=openfile)
    mainMenu.add_separator()
    mainMenu.add_command(label="Exit", command=main_gui_window.destroy)
    menu.add_cascade(menu=mainMenu, label="File")
    # -- Options menu -- #
    optionsMenu = tk.Menu(menu)
    optionsMenu.add_command(label="Compress", command=compress_gui)
    optionsMenu.add_command(label="Compare fingerprints", command=compare_gui)
    menu.add_cascade(menu=optionsMenu, label="Options")

def openfile():
    global_variables['main_window'].destroy()
    init_screen()

def update_image(img):
    global_variables['working_image'] = img
    photo = ImageTk.PhotoImage(img)
    global_variables['image_label'].configure(image=photo)
    global_variables['image_label'].image = photo

def compress_gui():
    image = global_variables['working_image']
    image = fingerprint.binary_threshold(image)
    string = fingerprint.compress(image)
    size = image.size
    name = global_variables['img_path'].split("/")[-1]

    # Save the file in the chosen directory
    indir = "../" + path.dirname(path.realpath(__file__))
    filename = tkFileDialog.asksaveasfilename(filetypes=[('TXT', '.txt')], initialfile='newfile.txt', initialdir=indir)
    if filename:
        output = open(filename, 'w')
        output.write(name + '\n')
        output.write(str(size[0]) + '\n')
        output.write(str(size[1]) + '\n')
        output.write(string)
        output.close()
        original_size = path.getsize(global_variables['img_path'])
        compressed_size = path.getsize(filename)
        ratio = round(original_size / (compressed_size * 1.0), 2)
        tkMessageBox.showinfo("", "Radio de compresion obtenido: " + str(ratio))

def compare_gui():
    image = global_variables['working_image']
    indir = "../" + path.dirname(path.realpath(__file__))
    directory = tkFileDialog.askdirectory(initialdir=indir)
    if directory:
        higher_match, message = fingerprint.compare(image, directory)
        results_window(higher_match, message)

def results_window(higher_match, message):
    results_window = tk.Toplevel()
    results_window.title("Resultados")
    results_window.resizable(0, 0)

    imageframe = tk.Frame(results_window)
    tk.Label(imageframe, text="Mejor coincidencia", pady=2, font="arial 14 bold").grid(column=0, row=0)
    img = Image.open(higher_match)
    img = rz.resize(img)
    photo = ImageTk.PhotoImage(img)
    tk.Label(results_window, image=photo).grid(column=0, row=1)
    imageframe.grid(column=0, row=0)

    resultsframe = tk.Frame(results_window)
    tk.Label(resultsframe, text="Otros resultados:", pady=2, font="arial 14 bold").grid(column=0, row=0)
    tk.Label(resultsframe, text=message, justify="left", padx=5, font="arial 12").grid(column=0, row=1)
    resultsframe.grid(column=1, row=1)

    results_window.mainloop()

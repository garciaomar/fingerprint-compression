import Tkinter as tk
import ttk
import tkFileDialog
import tkMessageBox
from os import path
import PIL
from PIL import Image, ImageTk
from utils import resize as rz
from src import fingerprint

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
    # Save the file in the chosen directory
    indir = "../" + path.dirname(path.realpath(__file__))
    filename = tkFileDialog.asksaveasfilename(filetypes=[('TXT', '.txt')], initialfile='newfile.txt', initialdir=indir)
    if filename:
        output = open(filename, 'w')
        output.write(str(size[0]) + '\n')
        output.write(str(size[1]) + '\n')
        output.write(string)
        output.close()

def decompress_gui():
    indir = "../" + path.dirname(path.realpath(__file__))
    v = tkFileDialog.askopenfile(initialdir=indir)
    if v:
        image = fingerprint.decompress(v.name)
        update_image(image)

def compare_gui():
    image = global_variables['working_image']
    indir = "../" + path.dirname(path.realpath(__file__))
    directory = tkFileDialog.askdirectory(initialdir=indir)
    if directory:
        message = fingerprint.compare(image, directory)
        tkMessageBox.showinfo("Resultados", message)
def decompress_main():
    indir = "../" + path.dirname(path.realpath(__file__))
    v = tkFileDialog.askopenfile(initialdir=indir)
    if v:
        image = fingerprint.decompress(v.name)

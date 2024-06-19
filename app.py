import shutil
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageTk
import os


class App(tk.Tk):
    def __init__(self, title, size):

        # main setup
        super().__init__()
        self.title(title)
        self.geometry(f'{size[0]}x{size[1]}')
        self.minsize(size[0], size[1])
        # self.resizable(False, False)
        self.image = None
        self.image_ratio = None
        self.image_tk = None
        self.water_mark = None

        # Menu
        self.menu = Menu(self)

        # Main
        self.main = Main(self)

        # run
        self.mainloop()

    # Load and place image
    def load_img(self, canvas: tk.Canvas):
        file_path = filedialog.askopenfilename(title='Open Image files', filetypes=[('Image Files', '*.png *.jpg '
                                                                                                    '*.jpeg *.gif '
                                                                                                    '*.bmp *.ico')])
        if file_path:
            self.load_image(file_path=file_path)
            self.display_img(canvas=canvas)

            if self.water_mark:
                CreateImage(image=self.image, mark=self.water_mark, canvas=canvas, parent=self)

    def load_image(self, file_path) -> Image.Image:
        if file_path:
            # get current width and height of canvas
            self.image = Image.open(file_path)
            self.image_ratio = self.image.size[0] / self.image.size[1]
            self.image_tk = ImageTk.PhotoImage(self.image)

    def stretch_img(self, event):
        if self.image:
            width = event.width
            height = event.height
            # calc ratio
            ratio = self.calc_ratio(canvas=self.main.canvas)
            # resize image
            new_img = self.image.resize((ratio[0], ratio[1]))
            self.image_tk = ImageTk.PhotoImage(new_img)
            self.main.canvas.create_image(int(event.width / 2),
                                          int(event.height / 2),
                                          image=self.image_tk,
                                          anchor='center')

    def display_img(self, canvas: tk.Canvas):
        # Calc canvas ratio
        ratio = self.calc_ratio(canvas)

        # create new img
        new_img = self.image.resize((ratio[0], ratio[1]))
        self.image_tk = ImageTk.PhotoImage(new_img)
        canvas.create_image(int(canvas.winfo_width() / 2),
                            int(canvas.winfo_height() / 2),
                            image=self.image_tk,
                            anchor='center')

    def calc_ratio(self, canvas):
        # Calc canvas ratio
        canvas_ratio = canvas.winfo_width() / canvas.winfo_height()
        if canvas_ratio < self.image_ratio:
            width = int(canvas.winfo_width())
            height = int(width / self.image_ratio)
        else:
            height = int(canvas.winfo_height())
            width = int(height * self.image_ratio)

        return [width, height]


class Menu(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.place(x=0, y=0, relwidth=0.15, relheight=1)
        self.create_widgets(parent)

    def create_widgets(self, parent: App):
        load_image = ttk.Button(self, text='Load Image')
        load_water_mark = ttk.Button(self, text='Load water mark')
        save_image = ttk.Button(self, text='Save Image')

        # create the grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure((0, 1, 2), weight=0)

        # place the widgets
        load_image.grid(row=0, column=0, sticky='ew', pady=5, padx=5)
        load_water_mark.grid(row=1, column=0, sticky='ew', pady=5, padx=5)
        save_image.grid(row=2, column=0, sticky='ew', pady=5, padx=5)

        # widgets functions
        load_image.config(command=lambda: parent.load_img(canvas=parent.main.canvas))
        load_water_mark.config(command=lambda: LoadWaterMarkImg(parent=parent))
        save_image.config(command=lambda: SaveImage(parent=parent))


class Main(ttk.Frame):
    def __init__(self, parent: App):
        super().__init__(parent)
        self.canvas = tk.Canvas(parent, bd=0, highlightthickness=0, relief='ridge')
        self.canvas.place(relx=0.15, y=0, relheight=1, relwidth=0.85)
        self.canvas.bind('<Configure>', parent.stretch_img)


class LoadWaterMarkImg:

    def __init__(self, parent: App):
        self.parent = parent
        self.open_file()

    def open_file(self,):
        if self.parent.water_mark:
            self.parent.water_mark = None
        selected_file = filedialog.askopenfilename(title='Open Watermark img', filetypes=[('Image Files', '*.png *.jpg '
                                                                                                    '*.jpeg *.gif '
                                                                                                    '*.bmp *.ico')])
        if selected_file:
            # get file name and project path
            file_name = f"watermark.{os.path.basename(selected_file).split('.')[1]}"
            project_path = os.path.dirname(os.path.abspath(__file__))

            # delete any watermark file
            self.delete_file()

            # create destination path within project path
            img_folder_path = os.path.join(project_path, 'img')
            destination_path = os.path.join(img_folder_path, file_name)

            # copy the file
            shutil.copy2(selected_file, destination_path)

            self.parent.water_mark = Image.open(f'img/{file_name}')

            if self.parent.image:
                CreateImage(image=self.parent.image, mark=self.parent.water_mark, canvas=self.parent.main.canvas, parent=self.parent)

    @staticmethod
    def delete_file():
        for file in os.listdir('img'):
            if file.split('.')[0] == 'watermark':
                os.remove(f'img/{file}')


class CreateImage:

    def __init__(self, image: Image, mark: Image, canvas, parent: App) -> Image:
        self.image = image
        self.mark = mark
        self.canvas = canvas
        self.parent = parent
        self.new_image()

    def new_image(self):
        mask = None
        if self.mark.mode in ('RGBA', 'LA'):
            mask = self.mark
        x = self.image.size[0] - self.mark.size[0] - 5
        y = self.image.size[1] - self.mark.size[1] - 5
        self.image.paste(self.mark, (x, y), mask=mask)
        self.parent.display_img(canvas=self.canvas)


class SaveImage:
    def __init__(self, parent: App):
        self.parent = parent
        file_extension = self.parent.image.filename.split('.')[1]
        if self.parent.image:
            files = [('Image Files', f'*.{file_extension} *.jpg ''*.jpeg *.gif ''*.bmp *.ico')]
            file_path = filedialog.asksaveasfilename(filetypes=files, defaultextension=files, title='Save Image')
            if file_extension in ("jpg", "jpeg"):
                save_format = "JPEG"
            else:
                save_format = file_extension
            self.parent.image.save(file_path, save_format)
            messagebox.showinfo(title='File Saved', message='File saved')
        else:
            messagebox.showerror("Error", "Load a Image First")

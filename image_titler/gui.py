import os
import tkinter as tk
import tkinter.filedialog

import pkg_resources
from PIL import ImageTk, Image

from image_titler.utilities import process_image, convert_file_name_to_title, save_copy


TRC_ICON = os.path.join(os.path.dirname(__file__), '../icons/the-renegade-coder-sample-icon.png')


class ImageTitlerMain(tk.Tk):
    def __init__(self):
        super().__init__()
        self.menu = ImageTitlerMenuBar(self)
        self.gui = ImageTitlerGUI(self, self.menu)

    def update_view(self):
        self.gui.update_view()


class ImageTitlerGUI(tk.Frame):

    def __init__(self, parent, menu, **kw):
        super().__init__(parent, **kw)
        self.menu = menu
        self.preview = ImageTitlerPreviewPane(self)
        self.option_pane = ImageTitlerOptionPane(self)
        self.set_layout()
        self.pack(anchor=tk.W)

    def set_layout(self):
        self.option_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES, padx=10, pady=5, anchor=tk.W)
        self.preview.pack(side=tk.RIGHT, fill=tk.BOTH, expand=tk.YES)

    def update_view(self):
        if self.menu.image_path:
            title = None
            if self.option_pane.title_state.get() == 1:
                title = self.option_pane.title_value.get()
            self._render_preview(title=title)

    def _render_preview(self, title=None):
        title = convert_file_name_to_title(self.menu.image_path, title=title)
        self.menu.current_edit = process_image(self.menu.image_path, title)
        maxsize = (1028, 1028)
        small_image = self.menu.current_edit.copy()
        small_image.thumbnail(maxsize, Image.ANTIALIAS)
        image = ImageTk.PhotoImage(small_image)
        self.preview.config(image=image)
        self.preview.image = image
        self.set_layout()


class ImageTitlerPreviewPane(tk.Label):

    def __init__(self, parent, **kw):
        super().__init__(parent, **kw)


class ImageTitlerOptionPane(tk.Frame):

    def __init__(self, parent: ImageTitlerGUI, **kw):
        super().__init__(parent, **kw)
        self.parent = parent
        self.title_state: tk.IntVar = tk.IntVar()
        self.title_value: tk.StringVar = tk.StringVar()
        self.init_option_pane()

    def init_option_pane(self):
        title_label = tk.Checkbutton(self, text="Title:", variable=self.title_state, command=self.parent.update_view)
        title_label.pack(side=tk.LEFT, anchor=tk.N)

        self.title_value.trace("w", lambda name, index, mode, sv=self.title_value: self.parent.update_view())
        title_entry = tk.Entry(self, textvariable=self.title_value)
        title_entry.pack(side=tk.LEFT, anchor=tk.N)


class ImageTitlerMenuBar(tk.Menu):

    def __init__(self, parent: ImageTitlerMain):
        super().__init__(parent)
        self.parent = parent
        self.image_path = None
        self.current_edit = None
        self.file_menu = None
        self.init_menu()

    def init_menu(self):
        menu = tk.Menu(self.parent)
        self.parent.config(menu=menu)

        self.file_menu = tk.Menu(menu, tearoff=0, postcommand=self.save_as_enabled)
        self.file_menu.add_command(label="New Image", command=self.new_image)
        self.file_menu.add_command(label="Save As", command=self.save_as)

        menu.add_cascade(label="File", menu=self.file_menu)

    def new_image(self):
        self.image_path = tk.filedialog.askopenfilename()
        self.parent.update_view()

    def save_as(self):
        output_path = tk.filedialog.askdirectory()
        save_copy(self.image_path, self.current_edit, output_path=output_path)

    def save_as_enabled(self):
        if self.current_edit:
            self.file_menu.entryconfig(1, state=tk.NORMAL)
        else:
            self.file_menu.entryconfig(1, state=tk.DISABLED)


def main():
    root = ImageTitlerMain()
    version = pkg_resources.require("image-titler")[0].version
    root.title(f"The Renegade Coder Image Titler {version}")
    root.iconphoto(False, tk.PhotoImage(file=TRC_ICON))
    root.mainloop()


if __name__ == '__main__':
    main()

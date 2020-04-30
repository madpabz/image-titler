import os
import tkinter as tk
import tkinter.filedialog
from typing import Optional

import pkg_resources
from PIL import ImageTk, Image

from image_titler.utilities import process_image, convert_file_name_to_title, save_copy, TIER_MAP

TRC_ICON = os.path.join(os.path.dirname(__file__), '../icons/the-renegade-coder-sample-icon.png')


class ImageTitlerMain(tk.Tk):
    """
    The main window. This overrides the root class of tk, so we can make a menu.
    The remainder of the GUI is contained within a frame.
    """

    def __init__(self):
        super().__init__()
        self.menu = ImageTitlerMenuBar(self)
        self.gui = ImageTitlerGUI(self, self.menu)
        self.gui.pack(anchor=tk.W)

    def update_view(self):
        self.gui.update_view()


class ImageTitlerGUI(tk.Frame):
    """
    The main content of the GUI. This contains the preview pane and the option pane.
    """

    def __init__(self, parent, menu, **kw):
        super().__init__(parent, **kw)
        self.menu = menu
        self.preview = ImageTitlerPreviewPane(self)
        self.option_pane = ImageTitlerOptionPane(self)
        self.logo_path = None
        self.set_layout()

    def set_layout(self):
        self.preview.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.BOTH)
        self.option_pane.pack(side=tk.LEFT, anchor=tk.NW)

    def update_view(self, *args):
        if self.menu.image_path:
            title = None
            tier = ""
            logo_path = None
            if self.option_pane.title_state.get() == 1:
                title = self.option_pane.title_value.get()
            if self.option_pane.tier_state.get() == 1:
                tier = self.option_pane.tier_value.get()
            if self.option_pane.logo_state.get() == 1:
                logo_path = self.menu.logo_path
            self._render_preview(title=title, tier=tier, logo_path=logo_path)
        self._render_logo(self.menu.logo_path)

    def _render_preview(self, title=None, tier="", logo_path=None):
        title = convert_file_name_to_title(self.menu.image_path, title=title)
        self.menu.current_edit = process_image(self.menu.image_path, title, tier=tier, logo_path=logo_path)
        maxsize = (1028, 1028)
        small_image = self.menu.current_edit.copy()
        small_image.thumbnail(maxsize, Image.ANTIALIAS)
        image = ImageTk.PhotoImage(small_image)
        self.preview.config(image=image)
        self.preview.image = image
        self.set_layout()

    def _render_logo(self, logo_path):
        if logo_path and logo_path != self.logo_path:
            self.logo_path = logo_path
            maxsize = (50, 50)
            small_image = Image.open(logo_path)
            small_image.thumbnail(maxsize, Image.ANTIALIAS)
            image = ImageTk.PhotoImage(small_image)
            self.option_pane.logo_value.config(image=image)
            self.option_pane.logo_value.image = image


class ImageTitlerPreviewPane(tk.Label):
    """
    The preview pane is a simple label which contains a preview of the
    image currently being edited.
    """

    def __init__(self, parent, **kw):
        super().__init__(parent, **kw)


class ImageTitlerOptionPane(tk.Frame):
    """
    The option pane contains a set of options that can be controlled when editing the image.
    Changes are reflected in the preview pane.
    """

    def __init__(self, parent: ImageTitlerGUI, **kw):
        super().__init__(parent, **kw)
        self.parent = parent
        self.title_state: tk.IntVar = tk.IntVar()
        self.title_value: tk.StringVar = tk.StringVar()
        self.tier_state: tk.IntVar = tk.IntVar()
        self.tier_value: tk.StringVar = tk.StringVar()
        self.logo_state: tk.IntVar = tk.IntVar()
        self.logo_value: Optional[tk.Label] = None
        self.init_option_pane()

    def init_option_pane(self):
        # Title UI
        title_frame = tk.Frame(self)
        title_label = tk.Checkbutton(title_frame, text="Title:", variable=self.title_state,
                                     command=self.parent.update_view)
        self.title_value.trace("w", self.parent.update_view)
        title_entry = tk.Entry(title_frame, textvariable=self.title_value)
        self.layout_option_row(title_frame, title_label, title_entry)

        # Tier UI
        tier_frame = tk.Frame(self)
        tier_label = tk.Checkbutton(tier_frame, text="Tier:", variable=self.tier_state,
                                     command=self.parent.update_view)
        self.tier_value.set(list(TIER_MAP.keys())[0])
        tier_option_menu = tk.OptionMenu(tier_frame, self.tier_value, *TIER_MAP.keys(), command=self.parent.update_view)
        self.layout_option_row(tier_frame, tier_label, tier_option_menu)

        # Logo UI
        logo_frame = tk.Frame(self)
        logo_label = tk.Checkbutton(logo_frame, text="Logo:", variable=self.logo_state, command=self.parent.update_view)
        self.logo_value = tk.Label(logo_frame, text="Select a logo using 'File' > 'New Logo'")
        self.layout_option_row(logo_frame, logo_label, self.logo_value)

    @staticmethod
    def layout_option_row(frame, label, value):
        frame.pack(side=tk.TOP, anchor=tk.NW, padx=10, pady=5, expand=tk.YES, fill=tk.X)
        label.pack(side=tk.LEFT)
        value.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)


class ImageTitlerMenuBar(tk.Menu):
    """
    The menu bar for interactions like loading files and logos. 
    """

    def __init__(self, parent: ImageTitlerMain):
        super().__init__(parent)
        self.parent = parent
        self.image_path = None
        self.logo_path = None
        self.current_edit = None
        self.file_menu = None
        self.init_menu()

    def init_menu(self):
        menu = tk.Menu(self.parent)
        self.parent.config(menu=menu)

        self.file_menu = tk.Menu(menu, tearoff=0, postcommand=self.save_as_enabled)
        self.file_menu.add_command(label="New Image", command=self.new_image)
        self.file_menu.add_command(label="New Logo", command=self.new_logo)
        self.file_menu.add_command(label="Save As", command=self.save_as)

        menu.add_cascade(label="File", menu=self.file_menu)

    def new_image(self):
        self.image_path = tk.filedialog.askopenfilename()
        self.parent.update_view()

    def new_logo(self):
        self.logo_path = tk.filedialog.askopenfilename()
        self.parent.update_view()

    def save_as(self):
        output_path = tk.filedialog.askdirectory()
        save_copy(self.image_path, self.current_edit, output_path=output_path)

    def save_as_enabled(self):
        if self.current_edit:
            self.file_menu.entryconfig(2, state=tk.NORMAL)
        else:
            self.file_menu.entryconfig(2, state=tk.DISABLED)


def main():
    root = ImageTitlerMain()
    version = pkg_resources.require("image-titler")[0].version
    root.title(f"The Renegade Coder Image Titler {version}")
    root.iconphoto(False, tk.PhotoImage(file=TRC_ICON))
    root.mainloop()


if __name__ == '__main__':
    main()

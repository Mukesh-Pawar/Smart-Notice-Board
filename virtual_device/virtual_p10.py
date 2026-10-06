import tkinter as tk
from config import WINDOW_TITLE


class VirtualP10:
    """
    Simulates two physical P10 panels connected side-by-side
    and used as ONE continuous display.

    Panel 1 = left half
    Panel 2 = right half

    The notice is rendered across the complete 128x16 virtual matrix,
    not duplicated on each panel.
    """

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry("1100x390")
        self.root.minsize(850, 330)

        self.canvas = tk.Canvas(
            self.root,
            bg="#111111",
            highlightthickness=0
        )
        self.canvas.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        self.status = tk.StringVar(
            value="Virtual ESP32 starting..."
        )

        tk.Label(
            self.root,
            textvariable=self.status,
            font=("Arial", 11)
        ).pack(pady=(0, 12))

        # Two physical P10 panels joined as one display.
        # Each panel is represented as 64 x 16.
        self.panel_cols = 64
        self.rows = 16
        self.total_cols = 128

        self.full_title = "SMART NOTICE BOARD"
        self.full_message = "Waiting for notice..."

        self.visible_title = ""
        self.visible_message = ""

        self.animation_id = None
        self.animation_index = 0
        self.animation_text = ""
        self.animation_target = "title"

        self.root.bind(
            "<Configure>",
            lambda event: self.draw()
        )

        self.draw()

    def set_status(self, text):
        self.status.set(text)

    def show_notice(self, title, message, priority=""):
        self.full_title = title or "SMART NOTICE BOARD"
        self.full_message = message or " "

        if self.animation_id is not None:
            try:
                self.root.after_cancel(self.animation_id)
            except Exception:
                pass

        self.visible_title = ""
        self.visible_message = ""

        self.animation_target = "title"
        self.animation_text = self.full_title
        self.animation_index = 0

        self.draw()
        self.type_next_letter()

    def clear_notice(self):
        if self.animation_id is not None:
            try:
                self.root.after_cancel(self.animation_id)
            except Exception:
                pass

        self.full_title = "NO ACTIVE NOTICE"
        self.full_message = "There is currently no active notice."

        self.visible_title = self.full_title
        self.visible_message = self.full_message

        self.draw()

    def type_next_letter(self):
        if self.animation_index < len(self.animation_text):
            visible = self.animation_text[
                :self.animation_index + 1
            ]

            if self.animation_target == "title":
                self.visible_title = visible
            else:
                self.visible_message = visible

            self.animation_index += 1
            self.draw()

            self.animation_id = self.root.after(
                90,
                self.type_next_letter
            )
            return

        # Title finished -> type message.
        if self.animation_target == "title":
            self.animation_target = "message"
            self.animation_text = self.full_message
            self.animation_index = 0

            self.animation_id = self.root.after(
                300,
                self.type_next_letter
            )
            return

        self.animation_id = None
        self.draw()

    def draw_led_matrix(self, x1, y1, x2, y2):
        """
        Draw one continuous 128x16 LED matrix.
        The vertical line at the middle only marks the physical
        connection between the two P10 panels.
        """
        width = x2 - x1
        height = y2 - y1

        cell_w = width / self.total_cols
        cell_h = height / self.rows

        for row in range(self.rows):
            for col in range(self.total_cols):
                px = x1 + col * cell_w + cell_w / 2
                py = y1 + row * cell_h + cell_h / 2
                radius = max(
                    1,
                    min(cell_w, cell_h) * 0.18
                )

                self.canvas.create_oval(
                    px - radius,
                    py - radius,
                    px + radius,
                    py + radius,
                    fill="#242424",
                    outline=""
                )

        # Physical seam between P10 #1 and P10 #2.
        seam_x = x1 + width / 2

        self.canvas.create_line(
            seam_x,
            y1,
            seam_x,
            y2,
            fill="#555555",
            width=3
        )

    def draw(self):
        if not self.root.winfo_exists():
            return

        self.canvas.delete("all")

        width = max(self.canvas.winfo_width(), 850)
        height = max(self.canvas.winfo_height(), 230)

        # One large display made from two panels.
        self.canvas.create_rectangle(
            0, 0, width, height,
            fill="#050505",
            outline="#444444",
            width=2
        )

        self.draw_led_matrix(
            0,
            0,
            width,
            height
        )

        # Text is centered across the COMPLETE 2-panel display.
        center_x = width / 2

        self.canvas.create_text(
            center_x,
            height * 0.30,
            text=self.visible_title[:80],
            fill="#ff3b30",
            font=("Courier New", 21, "bold")
        )

        self.canvas.create_text(
            center_x,
            height * 0.63,
            text=self.visible_message[:150],
            fill="#ff3b30",
            font=("Courier New", 15, "bold"),
            width=width - 70
        )


if __name__ == "__main__":
    display = VirtualP10()
    display.show_notice(
        "TEST NOTICE",
        "Two P10 panels working as one continuous display."
    )
    display.root.mainloop()

import time
import configparser
import tkinter as tk
from tkinter import messagebox
from recorder import Recorder


class Setting:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config["Recorder"] = {
            "saveFolder": "",
            "format": "",
            "sampleRate": "",
            "bitrate": "",
        }

    def read_setting(self, filepath: str):
        """讀取設定"""

    def write_setting(self, filepath: str):
        """寫入設定"""


class UI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Recorder")
        self.geometry("280x150")
        self.resizable(False, False)
        self.iconbitmap("./img/icon.ico")


        self.padx = 10
        self.pady = 10
        self.grid_columnconfigure(index=0, weight=1)
        self.grid_rowconfigure(index=0, weight=4)
        self.grid_rowconfigure(index=1, weight=1)

        # upper frame
        self.frame_indicator = tk.Frame(self)
        self.frame_indicator.grid(
            column=0, row=0, sticky="nsew", padx=self.padx, pady=self.pady
        )
        self.frame_indicator.grid_columnconfigure(index=0, weight=2)
        self.frame_indicator.grid_columnconfigure(index=1, weight=3)
        self.frame_indicator.grid_rowconfigure(index=0, weight=1)

        # record button
        img_size = 10
        self.img_record = tk.PhotoImage(file="./img/record.png")
        self.img_record.zoom(img_size, img_size)
        self.img_stop = tk.PhotoImage(file="./img/stop.png")
        self.img_stop.zoom(img_size, img_size)
        
        self.btn_record = tk.Button(self.frame_indicator, image=self.img_record, command=self.record_stop_action)
        self.btn_record.config(height=img_size * 7, width=img_size * 7, borderwidth=0,  highlightthickness=0)
        self.btn_record.grid(
            column=0, row=0, padx=self.padx, pady=self.pady, sticky="ns"
        )

        # record Timer
        self.label_timer = tk.Label(
            self.frame_indicator, text="00:00:00", font=("Arial", 20)
        )
        self.label_timer.grid(column=1, row=0)

        # bottom frame
        self.frame_setting = tk.Frame(self)
        self.frame_setting.grid(
            column=0, row=1, sticky="nsew", padx=self.padx, pady=self.pady
        )
        self.frame_setting.grid_columnconfigure(0, weight=1)
        self.frame_setting.grid_rowconfigure(0, weight=1)

        # audio source
        self.list_temp = ["Record Source"]
        self.list_audio_source = tk.StringVar()
        self.list_audio_source.set(self.list_temp[0])
        self.menu_audio_source = tk.OptionMenu(
            self.frame_setting, self.list_audio_source, *self.list_temp
        )
        self.menu_audio_source.config()
        self.menu_audio_source.grid(column=0, row=0, columnspan=3, sticky="ew")

        self.init_recorder()
        self._update_device_menu()

    def init_recorder(self):
        self.isRec = False
        self.timer = 0
        self.rec = Recorder()

    def _update_device_menu(self):
        menu = self.menu_audio_source["menu"]
        menu.delete(0, "end")
        devices = self.rec.get_mics()
        for _, d in enumerate(devices):
            menu.add_command(
                label=d, command=lambda value=d: self.list_audio_source.set(value)
            )
        self.list_audio_source.set(devices[0])

    def _update_timer(self):
        if self.isRec:
            self.timer += 1
            minutes, seconds = divmod(self.timer, 60)
            hours, minutes = divmod(minutes, 60)
            time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            self.label_timer.config(text=time_str)
            self.after(1000, self._update_timer)  # 每1000毫秒更新一次

    def _clear_timer(self):
        self.timer = 0
        self.label_timer.config(text = "00:00:00")

    def _on_closing(self):
        if messagebox.askokcancel("Quit", "Are you sure?"):
            self._stop_record()
            self.destroy()

    def record_stop_action(self):
        if self.isRec:
            self.isRec = False
            self._stop_record()
            time.sleep(1/2) # prevent toggle too fast
        else:
            self.isRec = True
            self._start_record()

    def _start_record(self):
        self._clear_timer()
        self.rec.record()
        self._update_timer()
        self.btn_record.config(image=self.img_stop)
        self.menu_audio_source.config(state="disabled")

    def _stop_record(self):
        self.rec._stop_record()
        self.btn_record.config(image=self.img_record)
        self.menu_audio_source.config(state="normal")


    def start(self):
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.mainloop()


def main():
    ui = UI()
    ui.start()


if __name__ == "__main__":
    main()

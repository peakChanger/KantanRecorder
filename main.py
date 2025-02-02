import base64
import uuid
import time
import tkinter as tk
from os import remove as osre
from tkinter import messagebox, ttk
from recorder import Recorder
from img.icon import imgIcon, imgStop, imgRecord

class UI(tk.Tk):
    def __init__(self):
        super().__init__() # 用於呼叫父類別的__init__()
        self.title("Recorder")
        self.geometry("280x150")
        self.resizable(False, False)
        self._set_icon()

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
        self.img_record = tk.PhotoImage(data = base64.b64decode(imgRecord))
        self.img_record.zoom(img_size, img_size)
        self.img_stop = tk.PhotoImage(data = base64.b64decode(imgStop))
        self.img_stop.zoom(img_size, img_size)

        self.btn_record = tk.Button(
            self.frame_indicator, image=self.img_record, command=self.record_stop_action
        )
        self.btn_record.config(
            height=img_size * 7, width=img_size * 7, borderwidth=0, highlightthickness=0
        )
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
        self.list_audio_source = ["Record Source"]
        self.combobox_audio_source = ttk.Combobox(
            self.frame_setting, values=self.list_audio_source, state="readonly"
        )
        self.combobox_audio_source.config()
        self.combobox_audio_source.grid(column=0, row=0, columnspan=3, sticky="ew")

        self.init_recorder()
        self._update_device_menu()

    def init_recorder(self):
        self.isRec = False
        self.timer = 0
        self.rec = Recorder()

    def _update_device_menu(self):
        self.list_audio_source = self.rec.get_mics()
        self.combobox_audio_source['values'] = self.list_audio_source
        self.combobox_audio_source.current(0)

    def _set_icon(self):
        tmpFileName = f"{str(uuid.uuid4())}.ico"
        with open(tmpFileName, 'wb+') as tmpIcon: 
            tmpIcon.write(base64.b64decode(imgIcon))
        self.iconbitmap(tmpFileName)
        osre(tmpFileName)

    def _popup_error(self, message:str):
        messagebox.showerror("Error", message)

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
        self.label_timer.config(text="00:00:00")

    def _on_closing(self):
        if messagebox.askokcancel("Quit", "Are you sure?"):
            self._stop_record()
            self.destroy()

    def record_stop_action(self):
        if self.isRec:
            self.isRec = False
            self._stop_record()
            time.sleep(1 / 2)  # prevent toggle too fast
        else:
            self.isRec = True
            self._start_record()

    def _start_record(self):
        self._clear_timer()
        self.rec.record(self.combobox_audio_source.current())
        self._update_timer()
        self.btn_record.config(image=self.img_stop)
        self.combobox_audio_source.config(state="disabled")

    def _stop_record(self):
        self.rec._stop_record()
        self.btn_record.config(image=self.img_record)
        self.combobox_audio_source.config(state="normal")

    def start(self):
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.mainloop()



def main():
    ui = UI()
    ui.start()


if __name__ == "__main__":
    main()

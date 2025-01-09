from os.path import isdir
from os import mkdir
import soundcard as sc
import wave
import datetime
import queue
import threading
import time
import numpy as np


class Recorder:
    def __init__(
        self, sample_rate: int = 44100, channels: int = 2, folder: str = "./kantanRecs"
    ):
        self.speaker = sc.default_speaker()
        self.mics = sc.all_microphones(include_loopback=True)
        self.defaulf_mic = self.mics[0]

        self.sample_rate = sample_rate
        self.format = "wav"
        self.channels = channels
        self.bandwidth = 2  # 2bytes = 16-bit
        self.bandwidth_int = 32767

        self.folder = folder

        self.stop_flag = False
        self.audio_queue = queue.Queue()

    def get_mics(self) -> list:
        self.mics = sc.all_microphones(include_loopback=True)
        return list(self.mics)

    def set_mic(self, index: int):
        self.defaulf_mic = self.mics[index]

    def record(self):
        def record_audio():
            with self.defaulf_mic.recorder(
                channels=self.channels,
                samplerate=self.sample_rate,
                blocksize=512,
                # exclusive_mode=True,
            ) as rc:
                while True:
                    data = rc.record(numframes=self.sample_rate)
                    # print(type(data), type(data[0]))
                    self.audio_queue.put(data)
                    if self.stop_flag:
                        self.audio_queue.put(None)
                        break

        def write_file():
            filename = self._gen_filename()
            with wave.open(filename, "w") as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.bandwidth)
                wf.setframerate(self.sample_rate)

                # TODO 解決錄音可能不連續
                while True:
                    time.sleep(1 / 2)
                    try:
                        audio_data = self.audio_queue.get()
                        if audio_data is None:
                            break
                        audio_data = (audio_data * self.bandwidth_int).astype(np.int16)
                        wf.writeframes(audio_data.tobytes())
                        # now = datetime.datetime.now().strftime("%H%M%S")
                        # print(now)
                    except queue.Empty:
                        pass

        self.stop_flag = False
        record_thread = threading.Thread(target=record_audio)
        save_thread = threading.Thread(target=write_file)

        # print("start")
        record_thread.daemon = True
        save_thread.daemon = True
        record_thread.start()
        save_thread.start()
        # try:
        #     while True:
        #         if self.stop_flag:
        #             break
        #         time.sleep(1)
        # except KeyboardInterrupt:
        #     # print("stop")
        #     self._stop_record()

    def _stop_record(self):
        self.stop_flag = True

    def _gen_filename(self) -> str:
        if not isdir(self.folder):
            mkdir(self.folder)
        now = datetime.datetime.now()
        timecode = now.strftime("%Y_%m%d_%H%M%S")
        return f"{self.folder}/{timecode}.{self.format}"


if __name__ == "__main__":
    rec = Recorder()
    rec.record()
    # print(list(rec.mics))

import os
from datetime import datetime

class PixelinkCamera:
    def __init__(self, camera_sn: str, ffmpeg_path: str = r"C:\\Program Files\\PixeLINK\\bin\\x64\\ffmpegPxL.exe"):
        self.camera_sn = camera_sn.strip()
        self.ffmpeg_path = ffmpeg_path
        self.output_base = os.path.join(os.getcwd(), "captures")
        os.makedirs(self.output_base, exist_ok=True)

    def _create_timestamp_folder(self):
        folder_name = datetime.now().strftime("%m%d_%H%M%S")
        folder_path = os.path.join(self.output_base, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path

    def capture_image(self):
        """
        This method is intended to run in a local environment where subprocess execution is supported.
        In restricted environments (e.g., browser sandboxes), this will not work.
        """
        import subprocess

        folder = self._create_timestamp_folder()
        bmp_path = os.path.join(folder, "capture.bmp")

        camera_arg = f"video={self.camera_sn}"

        cmd = [
            self.ffmpeg_path,
            "-f", "dshow",
            "-i", camera_arg,
            "-frames:v", "1",
            bmp_path
        ]

        try:
            subprocess.run(cmd, check=True)
            return bmp_path
        except FileNotFoundError:
            raise RuntimeError(f"ffmpeg executable not found at: {self.ffmpeg_path}")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to capture image: {e}")
        except OSError as e:
            raise RuntimeError("Subprocess execution is not supported in this environment.\n"
                               "Please run this script on a local machine with access to the Pixelink camera.")


# Example usage:
if __name__ == "__main__":
    cam = PixelinkCamera("PixelLINK USB3 Camera Release 4")
    try:
        output_file = cam.capture_image()
        print(f"Image saved at: {output_file}")
    except RuntimeError as err:
        print(f"Error: {err}")

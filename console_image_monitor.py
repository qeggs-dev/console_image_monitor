import os
import sys
import time
import queue
import argparse
import threading
import numpy as np

from PIL import Image
from enum import StrEnum

class ImageResizeType(StrEnum):
    FILL = "fill"
    WIDTH = "width"
    HEIGHT = "height"

class ImageResizeMode(StrEnum):
    NEAREST = "nearest"
    BOX = "box"
    BILINEAR = "bilinear"
    HAMMING = "hamming"
    BICUBIC = "bicubic"
    LANCZOS = "lanczos"

class ConsoleImageMonitor:
    @staticmethod
    def read_image(open_path: str | os.PathLike):
        return Image.open(open_path)
    
    @classmethod
    def show_image(cls, image: Image.Image, alpha_charset: str = " ░▒▓█", color_reverse: bool = False):
        image = image.convert('RGBA')
        img_array = np.array(image)
        if color_reverse:
            inverted_array = 255 - img_array
            image = Image.fromarray(inverted_array)
        x, y = image.size
        show_x, show_y = os.get_terminal_size()
        if x > show_x or y > show_y:
            image = cls.center_crop(image, show_x, show_y)
        
        # Update image size
        x, y = image.size
        
        pixels = image.load()
        try:
            sys.stdout.write(f"\033[?25l") # Hide cursor
            for pixel_y in range(y):
                line_buffer: list[str] = []
                for pixel_x in range(x):
                    pixel = pixels[pixel_x, pixel_y]
                    red, green, blue, alpha = pixel
                    alpha = alpha / 255.0
                    char = alpha_charset[int(alpha * (len(alpha_charset) - 1))]
                    line_buffer.append((pixel_x, pixel_y, f"\033[38;2;{red};{green};{blue}m{char}\033[0m"))
                sys.stdout.write("".join([char for x, y, char in line_buffer]))
                sys.stdout.write("\n")
        finally:
            sys.stdout.write("\033[?25h") # Show cursor
            sys.stdout.write("\033[0m")
            sys.stdout.flush()
    
    @classmethod
    def show_image_random(cls, image: Image.Image, alpha_charset: str = " ░▒▓█", color_reverse: bool = False, worker: int = 10):
        image = image.convert('RGBA')
        img_array = np.array(image)
        if color_reverse:
            inverted_array = 255 - img_array
            image = Image.fromarray(inverted_array)
        x, y = image.size
        show_x, show_y = os.get_terminal_size()
        if x > show_x or y > show_y:
            image = cls.center_crop(image, show_x, show_y)
        
        # Update image size
        x, y = image.size
        
        pixels = image.load()
        threads: list[threading.Thread] = []
        data_lock = threading.Lock()
        submited: set[tuple[int, int]] = set()
        processed: queue.Queue[tuple[int, int, str]] = queue.Queue()
        finished = threading.Event()
        start = threading.Event()
        try:
            sys.stderr.write(f"\033[?25l") # Hide cursor
            def line_render():
                while True:
                    with data_lock:
                        if len(submited) == 0:
                            if finished.is_set():
                                break
                            time.sleep(0.05)
                            continue
                        pixel_x, pixel_y = submited.pop()
                    pixel = pixels[pixel_x, pixel_y]
                    red, green, blue, alpha = pixel
                    alpha = alpha / 255.0
                    char = alpha_charset[int(alpha * (len(alpha_charset) - 1))]
                    processed.put((pixel_x, pixel_y, f"\033[38;2;{red};{green};{blue}m{char}\033[0m"))
            
            def printer():
                sys.stderr.write("\n" * y)
                while True:
                    try:
                        pixel_x, pixel_y, content = processed.get(timeout=0.1)
                    except queue.Empty:
                        if finished.is_set():
                            break
                        continue
                    sys.stderr.write(f"\033[{pixel_y};{pixel_x}H")
                    sys.stderr.write(content)
            
            for index in range(worker):
                thread = threading.Thread(target=line_render, daemon=True)
                thread.start()
                threads.append(thread)
            
            printer_thread = threading.Thread(target=printer, daemon=True)
            
            for pixel_y in range(y):
                for pixel_x in range(x):
                    submited.add((pixel_x, pixel_y))
            
            printer_thread.start()
            start.set()
            
            finished.set()

            for thread in threads:
                thread.join()

            printer_thread.join()
            
            sys.stderr.flush()
        finally:
            sys.stderr.write("\033[?25h") # Show cursor
            sys.stderr.write("\033[0m")
            sys.stderr.write(f"\033[0;0m")
            # sys.stderr.write("\n" * y)
            sys.stderr.flush()
    
    def center_crop(img: Image.Image, crop_width: int, crop_height: int) -> Image.Image:
        width, height = img.size
        
        left = (width - crop_width) // 2
        top = (height - crop_height) // 2
        right = left + crop_width
        bottom = top + crop_height
        
        left = max(0, left)
        top = max(0, top)
        right = min(width, right)
        bottom = min(height, bottom)
        
        return img.crop((left, top, right, bottom))
    
    @staticmethod
    def resize_image(image: Image.Image, resize_type: ImageResizeType, mode: ImageResizeMode, target_width: int, target_height: int):
        width, height = image.size
        match mode:
            case ImageResizeMode.NEAREST:
                resampling_mode = Image.Resampling.NEAREST
            case ImageResizeMode.BOX:
                resampling_mode = Image.Resampling.BOX
            case ImageResizeMode.BILINEAR:
                resampling_mode = Image.Resampling.BILINEAR
            case ImageResizeMode.HAMMING:
                resampling_mode = Image.Resampling.HAMMING
            case ImageResizeMode.BICUBIC:
                resampling_mode = Image.Resampling.BICUBIC
            case ImageResizeMode.LANCZOS:
                resampling_mode = Image.Resampling.LANCZOS
        
        if resize_type == ImageResizeType.FILL:
            return image.resize((target_width, target_height), resampling_mode)
        
        elif resize_type == ImageResizeType.WIDTH:
            ratio = height / width
            new_height = int(target_width * ratio)
            return image.resize((target_width, int(new_height / 2)), resampling_mode)
        
        elif resize_type == ImageResizeType.HEIGHT:
            ratio = width / height
            new_width = int(target_height * ratio)
            return image.resize((new_width * 2, target_height), resampling_mode)
        
        else:
            raise ValueError("Invalid resize type.")

def init_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Monitor a image in the console.")
    parser.add_argument("-s", "--source", required=True, type = str, help="The source image path.")
    parser.add_argument("-rt", "--resize-type", type=ImageResizeType, default=ImageResizeType.FILL, help="The resize mode to use when displaying images in the console.")
    parser.add_argument("-rm", "--resize-mode", type=ImageResizeMode, default=ImageResizeMode.LANCZOS, help="The resize mode to use when displaying images in the console.")
    parser.add_argument("-ac", "--alpha-charset", type=str, default=" ░▒▓█", help="The charset to use for displaying alpha transparency.")
    parser.add_argument("-cr", "--color-reverse", action="store_true", help="Reverse the color of the image.")
    parser.add_argument("-w", "--workers", type=int, default=10, help="The number of workers to use for rending images.")
    parser.add_argument("-r", "--random-render", action="store_true", help="Render images randomly.")
    return parser

def main():
    parser = init_argparser()
    args = parser.parse_args()
    console_image_monitor = ConsoleImageMonitor()
    image = console_image_monitor.read_image(args.source)
    size_x, size_y = os.get_terminal_size()
    image_x, image_y = image.size
    if image_x > size_x or image_y > size_y:
        display_image = console_image_monitor.resize_image(
            image,
            args.resize_type,
            args.resize_mode,
            os.get_terminal_size().columns,
            os.get_terminal_size().lines,
        )
    
    if args.random_render:
        console_image_monitor.show_image_random(
            display_image,
            args.alpha_charset,
            args.color_reverse,
            args.workers
        )
    else:
        console_image_monitor.show_image(
            display_image,
            args.alpha_charset,
            args.color_reverse,
        )

if __name__ == "__main__":
    main()
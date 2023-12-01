# -*- coding: utf-8 -*-
import pygame
import time
import subprocess
import threading
from io import BytesIO
from PIL import Image
import cv2
import numpy as np
try:
    import picamera2
except ImportError:
    picamera2 = None  # picamera is optional

try:
    import picamera
except ImportError:
    picmera = None
from LDS.language import get_translated_text
from LDS.camera.base import BaseCamera


def get_rpi_camera_proxy(port=None):
    """Return camera proxy if a Raspberry Pi compatible camera is found
    else return None.

    :param port: look on given port number
    :type port: int
    """
    if not picamera2:
        return None 
    # try:
    #     process = subprocess.Popen(['v4l2-ctl'])
    
    return picamera2


class RpiCamera(BaseCamera):

    """Camera management
    """

    
    if picamera:
        IMAGE_EFFECTS = list(picamera.PiCamera.IMAGE_EFFECTS.keys())
    else:
        IMAGE_EFFECTS = []
    
    

    def _specific_initialization(self):
        """Camera initialization.
        """
        self._cam = picamera2.Picamera2()
        self.framerate = 15  # Slower is necessary for high-resolution
        self.video_stabilization = True
        self.vflip = False
        self.hflip = self.capture_flip
        self.resolution = self.resolution
        self.iso = self.preview_iso
        self.rotation = self.preview_rotation
        self._preview = None
        self.event = threading.Event()

    def _show_overlay(self, text, alpha):
        """Add an image as an overlay.
        """
        if self._window:  # No window means no preview displayed
            rect = self.get_rect()
            
            # Create an image padded to the required size (required by picamera)
            size = (((rect.width + 31) // 32) * 32, ((rect.height + 15) // 16) * 16)
            image = self.build_overlay(size, str(text), alpha)

            self._overlay = pygame.image.fromstring(image.tobytes(), image.size, 'RGBA')
            

    def _hide_overlay(self):
        """Remove any existing overlay.
        """
        if self._overlay:
            self._overlay = None

    def _post_process_capture(self, capture_data):
        """Rework capture data.

        :param capture_data: binary data as stream
        :type capture_data: :py:class:`io.BytesIO`
        """
        # "Rewind" the stream to the beginning so we can read its content
        capture_data.seek(0)
        return Image.open(capture_data)

    def preview(self, window, flip=True):
        """Display a preview on the given Rect (flip if necessary).
        """
        
        if self._cam._preview is not None:
            # Already running
            return
        
        
        
        # When a preview is initiated, pass window to the self._window parameter
        self._window = window
        window_rect = window.get_rect()
        

        rect = self.get_rect()
        # Create preview window width and height
        preview_window = rect.width, rect.height
        print("Rectangle size For window preview:", rect)
        # Do this to allow the app maintain its dimensions
        res = window_rect.width, window_rect.height
        # screen = pygame.display.set_mode(res)
        screen = self._window.surface
        
        # if self._cam.hflip:
        if flip:
            # Don't flip again, already done at init
            flip = False
        else:
            # Flip again because flipped once at init
            flip = True

        # stop camera before reconfiguration
        self._cam.stop()
        # Also stop camera before stopping x thread
        
        # Start preview using defined function from Picamera2
        self._cam.preview_configuration.main.size = preview_window
        self._cam.preview_configuration.main.format = 'BGR888'
        self._cam.configure("preview")
        self._cam.start()
        
        pos_x = res[0]/2 - preview_window[0]/2
        pos_y = res[1]/2 - preview_window[1]/2

        # Create attributes to be accessed by other methods
        self.pos_x = pos_x 
        self.pos_y = pos_y
        self.screen = screen

        x = threading.Thread(target=self.preview_update, args=(self.event, preview_window, screen, pos_x, pos_y))
        # Chreck if thread is alive before starting it
            
        if not (x.is_alive()):
            print("Thread is not alive")
            x.start()
        

    def preview_update(self, event, res, screen, x, y):
        while True:
            if event.is_set():
                break
            array = self._cam.capture_array()
            img = pygame.image.frombuffer(array.data, res, 'RGB')
            screen.blit(img, (x, y))
            if self._overlay:
                screen.blit(self._overlay, (x, y))
            pygame.display.update()
        print("After Starting Successfully")

    def preview_countdown(self, timeout, alpha=60):
        """Show a countdown of `timeout` seconds on the preview.
        Returns when the countdown is finished.
        """
        timeout = int(timeout)
        if timeout < 1:
            raise ValueError("Start time shall be greater than 0")
        if not self._cam._preview:
            raise EnvironmentError("Preview shall be started first")

        while timeout > 0:
            self._show_overlay(timeout, alpha)
            print("timeout:", timeout)
            time.sleep(1)
            timeout -= 1
            self._hide_overlay()

        self._show_overlay(get_translated_text('smile'), alpha)

    def preview_wait(self, timeout, alpha=60):
        """Wait the given time.
        """
        time.sleep(timeout)
        self._show_overlay(get_translated_text('smile'), alpha)

    def stop_preview(self):
        """Stop the preview.
        """
        self._hide_overlay()
        self._cam.stop_preview()
        self._window = None
        

    def capture(self, effect=None):
        """Capture a new picture in a file.
        """

        # Create still configuration to capture file

        effect = str(effect).lower()
        if effect not in self.IMAGE_EFFECTS:
            raise ValueError("Invalid capture effect '{}' (choose among {})".format(effect, self.IMAGE_EFFECTS))

        try:
            if self.capture_iso != self.preview_iso:
                self.iso = self.capture_iso
            if self.capture_rotation != self.preview_rotation:
                self.rotation = self.capture_rotation

            # Create a buffer in memory to hold the images
            stream = BytesIO()
            # Create effect for the snapshot
            self._cam.image_effect = effect
            # Capture image in the buffer using Picamera2.capture_file
            self._cam.capture_file(stream, format='jpeg')
            # self._cam.capture(stream, format='jpeg')

            if self.capture_iso != self.preview_iso:
                self.iso = self.preview_iso
            if self.capture_rotation != self.preview_rotation:
                self.rotation = self.preview_rotation

            # # Experiment converting to grayscale
            img = Image.open(stream)
            # # if img.mode == 'L':
            img = img.convert('L')
            # # img.save(stream, format='jpeg')
            stream2 = BytesIO()
            img.save(stream2, format='jpeg')
            # # stream = np.array(img)[...,::-1]
            # # Add the buffer with the image to a list of images
            # print("Image type:", type(img))
            # print("Image shape", img.size)
            # print("Stream type:", type(stream2))
            self._gray_captures.append(stream2)
            self._captures.append(stream)
        
        finally:
            self._cam.image_effect = 'none'

        self._hide_overlay()  # If stop_preview() has not been called

    def quit(self):
        """Close the camera driver, it's definitive.
        """
        self._cam.close()

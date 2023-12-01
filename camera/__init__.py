# -*- coding: utf-8 -*-

from LDS.utils import LOGGER
from LDS.camera.rpi import RpiCamera, get_rpi_camera_proxy
from LDS.camera.opencv import CvCamera, get_cv_camera_proxy



def close_proxy(rpi_cam_proxy, gp_cam_proxy=None, cv_cam_proxy=None):
    """Close proxy drivers.
    """
    if rpi_cam_proxy:
        RpiCamera(rpi_cam_proxy).quit()
    if cv_cam_proxy:
        CvCamera(cv_cam_proxy).quit()


def find_camera():
    """Initialize the camera depending of the connected one. The priority order
    is chosen in order to have best rendering during preview and to take captures.
    The gPhoto2 camera is first (drivers most restrictive) to avoid connection
    concurence in case of DSLR compatible with OpenCV.
    """
    rpi_cam_proxy = get_rpi_camera_proxy()
    print(rpi_cam_proxy)
    cv_cam_proxy = get_cv_camera_proxy()

    if rpi_cam_proxy:
        LOGGER.info("Configuring Picamera camera ...")
        close_proxy(None)
        rpi_camera = RpiCamera(rpi_cam_proxy)
        return rpi_camera
    elif cv_cam_proxy:
        LOGGER.info("Camera Not Found ...")
        return CvCamera(cv_cam_proxy)

    raise EnvironmentError("Neither Raspberry Pi nor GPhoto2 nor OpenCV camera detected")

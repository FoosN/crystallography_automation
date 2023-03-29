import os
import numpy
import logging
import imageio
import scipy.ndimage
# import matplotlib
# matplotlib.use("Agg", warn=False)
import matplotlib.pyplot as pyplot
import pylab
from skimage import measure

logging.basicConfig(level=logging.INFO)

def autoMesh(
    snapshot_dir,
    workflow_working_dir,
    auto_mesh_working_dir,
    prefix="snapshot",
    debug=False,
):
    x1_pixels = None
    y1_pixels = None
    dx_pixels = None
    dy_pixels = None
    delta_phiz = None
    std_phiz = None
    image_path = None
    os.chmod(auto_mesh_working_dir, 0o755)
    dict_loop = {}
    omega = 0
    logging.info("Analysing snapshot image at omega = %d degrees" % omega)
    image_path = os.path.join(snapshot_dir, "%s_%03d.png" % (prefix, omega))
    raw_img = readImage(image_path)

    if debug:
        plot_img(
            raw_img,
            os.path.join(auto_mesh_working_dir, "rawImage_%03d.png" % omega),
         )

    contours, contours_size = dropContourRecognition(raw_img)
    max_contours = findLargestContour(contours, contours_size)

    if debug:    
    # save the image and plot all the contours
        fig, ax = pyplot.subplots()
        ax.imshow(raw_img, cmap=pyplot.cm.gray)
        ax.plot(max_contours[:, 1], max_contours[:, 0], linewidth=2) # in 1 is X and in 0 is Y
        ax.axis('image')
        pyplot.savefig(
        os.path.join(auto_mesh_working_dir, "shapePlot_%03d.png" % omega)
       )

    x1_pixels, y1_pixels, dx_pixels, dy_pixels = findXYpixelCoord(max_contours)
    return x1_pixels, y1_pixels, dx_pixels, dy_pixels


def plot_img(img, plot_path):
    imgshape = img.shape
    extent = (0, imgshape[1], 0, imgshape[0])
    _ = pyplot.imshow(img, extent=extent)
    pyplot.gray()
    pyplot.colorbar()
    pyplot.savefig(plot_path)
    pyplot.close()
    return

""" def gridInfoToPixels(grid_info, pixels_per_mm):
    x1_pixels = grid_info["x1"] * pixels_per_mm  # grid infor as to be in mm (should come from MD I guess)
    y1_pixels = grid_info["y1"] * pixels_per_mm
    dx_pixels = grid_info["dx_mm"] * pixels_per_mm
    dy_pixels = grid_info["dy_mm"] * pixels_per_mm
    return (x1_pixels, y1_pixels, dx_pixels, dy_pixels) """

def readImage(image_path):
    if image_path.endswith(".png"):
        image = imageio.imread(image_path, as_gray=True)
    elif image_path.endswith(".npy"):
        image = numpy.load(image_path)
    return image  #it's an array

def dropContourRecognition(drop_img):
    # Find contours at a value of (max(image) + min(image)) / 2 (optionally possible to use float)
    contours = measure.find_contours(drop_img)
    contours_size = len(contours)
    return contours, contours_size

def findLargestContour(contours, contours_size):
    # find the largest array (should be the loop contours)
    max_contours_size = len(contours[0])
    for i in range (1, contours_size):
        if len(contours[i]) > max_contours_size:
            max_contours_size = len(contours[i])  
            max_contours = contours[i]         
    return max_contours
   
def findXYpixelCoord(max_contours):    
    #find min and max value for x and y
    x1_pixels = numpy.max(max_contours[:,1])
    y1_pixels = numpy.max(max_contours[:,0])
    x_min = numpy.min(max_contours[:,1])
    y_min = numpy.min(max_contours[:,0])
    # find delta betwee x_max and x_min 
    dx_pixels = x1_pixels - x_min
    dy_pixels = y1_pixels - y_min
    return (
        x1_pixels,
        y1_pixels,
        dx_pixels,
        dy_pixels)
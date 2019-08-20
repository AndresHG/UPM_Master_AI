
__author__ = "PMN"

import numpy as np
from numpy import linalg as la
from scipy import ndimage
import matplotlib.pyplot as ppl
import re
import pdb

from mpl_toolkits.mplot3d import Axes3D


def skew(v):
    """Compute the skew-symmetric matrix of a vector."""
    A = np.array([ [0, -v[2], v[1]], 
                [v[2], 0, -v[0]],
                [-v[1], v[0], 0] ])
    return A

def epipoles(F):
    """Compute the epipoles given the fundamental matrix."""
    U, D, V = la.svd(F)
    e1 = V.T[:,-1]
    e2 = U[:,-1]
    
    return e1, e2

def rodrigues(v):
    """
    The rodrigues' rotation formula.
    
    This function transforms a rotation vector to a rotation matrix.
    """
    theta = la.norm(v)
    if theta < 1e-15:
        return np.eye(3)
    
    alpha = np.cos(theta)
    beta = np.sin(theta)
    gamma = 1-np.cos(theta)
    omega = v/theta
    omegav = skew(omega)
    A = np.dot(omega[np.newaxis].T, omega[np.newaxis])
    return np.eye(3)*alpha + omegav*beta + A*gamma


def rgb2gray(img):
    """Convert a RGB image to gray scale."""
    return 0.2989*img[:,:,0] + 0.587*img[:,:,1] + 0.114*img[:,:,2]

def plot3D(x, y, z, *args):
    
    fig = ppl.gcf()
    ax = Axes3D(fig)
    ax.plot3D(x, y, z, *args)
    ppl.draw()
    return ax

def plothom(points, *args, **kwargs):
    """Plot a set of points given in homogeneous coordinates."""
    p = points / points[2,:]
    return ppl.plot(p[0,:], p[1,:], *args, **kwargs)


def matarray(*args, **kwargs):
    """
    Construct a 2D array using a Matlab-like notation.
    You can specify the separator element using the keyword
    argument 'sep'. By default, it is 'None'. This is
    useful when creating block matrices.
    
    When the resulting matrix has only one element, matarray
    will return the element.
    
    Examples:
    >>> matarray(1,2,None,3,4)
    array([[1, 2],
           [3, 4]])
    >>> matarray(1, 2, '', 3, 4, sep='')
    array([[1, 2],
          [3, 4]])
    >>> R = np.ones((3,3))
    >>> t = np.zeros((3,1))
    >>> matarray(R, t, None, 0, 0, 0, 1)
    array([[ 1.,  1.,  1.,  0.],
           [ 1.,  1.,  1.,  0.],
           [ 1.,  1.,  1.,  0.],
           [ 0.,  0.,  0.,  1.]])
    >>> matarray([3])
    3
    """
    sep = None
    arr = list(args)
    if len(arr) == 1:
        arr = arr[0]
    
    if not isinstance(arr, list):
        return arr
    
    if "sep" in kwargs:
        sep = kwargs["sep"]
    
    res = []
    aux = []
    for e in arr:
        if type(e) == type(sep):
            if e == sep:
                # New row.
                if len(aux) > 0:
                    res.append(np.hstack(aux))
                aux = []
        elif hasattr(e, '__iter__'):
            # Sub-matrix.
            submat = matarray(e, sep=sep)
            if submat is not None:
                aux.append(submat)
        else:
            aux.append(e)
    
    if len(aux) > 0:
        res.append(np.hstack(aux))
    if len(res) > 0:
        res = np.vstack(res)
        # If res has only one element, return the element.
        if res.size == 1:
            return res[0,0]
        return res
    
    return None


def projmat2rectify(P1, P2, prm2f, imsize, disp=0):
    """
    Determine the transformation for the epipolar rectification.
    
    Given the projection matrices of an stereo pair and the size
    of the images from the cameras, this function returns a pair
    of linear transformations (i.e., homographies) which rectify
    the images so that the epipolar lines correspond to the scanlines.
    
    Parameters
    ----------
    P1, P2 : ndarray
        Projection matrices of the cameras.
    prm2f: function that computes the fundamental matrix from two projection matrices (ej. 3)
    imsize : tuple
        The size of the image (height, width)
    disp : optional, int
        If given, it defines the horizontal displacement to be applied
        to the right image. If positive, the image will be displaced
        to the right; if negative, to the left.
    """
     
    imsize = np.asarray(imsize)
    F = prm2f(P1, P2)
    M = np.dot(P2, la.pinv(P1))
    border = np.array([[0, 0, 1], 
                        [imsize[1], 0, 1], 
                        [0, imsize[0], 1], 
                        [imsize[1], imsize[0], 1]]).T
    # Epipoles
    [e1,e2] = epipoles(F)
    # Compute the rotation which takes the epipole 2 to (f,0,1)
    e2r = e2[0:2]/la.norm(e2[0:2])
    p = np.array([[1, 0]]).T
    aux = matarray(e2r, None, p.T)
    v = np.array([0, 0, np.sign(la.det(aux))])
    v = v * np.arccos(np.dot(e2r,p))
    R = rodrigues(v)
    # Compute the transformation which takes the epipole to (f,0,0)
    e2r = np.dot(R, e2)
    e2r = e2r/e2r[-1]
    G = np.eye(3)
    G[2,0] = -1.0/e2r[0]
    H2 = np.dot(G,R)
    
    # The top left point in image 2 should be (0,0) after the transformation.
    border2 = hom2cart(np.dot(H2, border))
    min2 = border2.min(1)
    destsize2 = border2.max(1) - min2
    scale2 = 2*imsize/destsize2
    aux1 = np.array([[scale2[0], 0, disp], 
                    [0, scale2[1], 0], 
                    [0, 0, 1]])
    aux2 = np.array([[1, 0, -min2[0]], 
                    [0, 1, -min2[1]],
                    [0, 0, 1]])
    H2 = np.dot(aux1, np.dot(aux2, H2))
    
    # Transformation for the first camera.
    H1 = np.dot(H2, M)
    # The top left point in image 1 should be (0,0) after the transformation.
    border1 = hom2cart(np.dot(H1, border))
    min1 = border1.min(1)
    aux1 = np.array([[1, 0, -min1[0]], 
                    [0, 1, 0], 
                    [0, 0, 1]])
    H1 = np.dot(aux1, H1)
    return H1, H2

def rectify_images(im1, im2, H1, H2):
    """
    Rectify two images with two homographies.
    
    The output images have the same shape.
    
    Parameters
    ----------
    im1, im2 : array-like
        Pair of images.
    H1, H2 : array-like
        Homographies (3x3 matrices).
    
    Return
    ------
    O1, O2 : ndarray
        The pair of input images after the rectification. It is
        guaranteed that O1 and O2 have the same size.
    """
    h, w = im1.shape[:2]
    border = np.array([ [0, 0, 1],
                        [w, 0, 1],
                        [0, h, 1],
                        [w, h, 1]]).T
    # Determine the common size for both images.
    border1 = hom2cart(np.dot(H1, border))
    border2 = hom2cart(np.dot(H2, border))
    size1 = np.round(border1.max(1))
    size2 = np.round(border2.max(1))
    sizer = matarray(size1[:,np.newaxis], size2[:,np.newaxis]).max(1)
    
    # Sample the images.
    out_region = [0, sizer[0], 0, sizer[1]]
    O1 = warp_hom(im1, H1, out_region=out_region)[0]
    O2 = warp_hom(im2, H2, out_region=out_region)[0]
    return O1, O2

def hom2cart(points):
    """Transform homogeneous coordinates to cartesian coordinates.
    
    Parameters
    ----------
    points : array-like
        A 3xN or 4xN array of N points given in homogeneous coordinates.
    
    Returns
    -------
    out : ndarray
        A 2xN or 3xN array with the points expressed in cartesian coordinates.
    """
    return points[:-1,:]/points[-1,:]

def warp_hom(img, H, in_region = None, out_region = None):
    """Warp an image with a given homography.
    
    Parameters
    ----------
    img : array_like
        The image to warp. It can be a color or a grayscale image.
    H : array_like
        The 3x3 homography.
    in_region : list
        The region of the initial image where the warping
        will be performed. It should be a four-element list with
        the format [x_min, x_max, y_min, y_max]. If this parameter
        is not given, the complete image will be warped.
    out_region : list
        The region of the warped image to be returned. It
        should be a four-element list with format [x_min, x_max, y_min, y_max].
        If this parameter is not given, warp_hom will return the
        complete warped image.
    
    Returns
    -------
    out : array_like
        Warped image.
    out_region : list
        The region which occupies the returned image.
    """
    if img.ndim == 2:
        img = img[:,:,np.newaxis]
    
    if in_region is None:
        in_region = [0, img.shape[1], 0, img.shape[0]]
    img = img[in_region[2]:in_region[3], in_region[0]:in_region[1], :]
    
    if out_region is None:
        border = array([[in_region[0], in_region[2], 1],
                        [in_region[1], in_region[2], 1],
                        [in_region[0], in_region[3], 1],
                        [in_region[1], in_region[3], 1]], np.float64).T
        outborder = hom2cart(np.dot(H, border))
        outmax = np.ceil(outborder.max(1))
        outmin = np.floor(outborder.min(1))
        out_region = [outmin[0], outmax[0], outmin[1], outmax[1]]
    
    X,Y = np.meshgrid(np.arange(out_region[0], out_region[1]),
                        np.arange(out_region[2], out_region[3]))
    points = np.ones((3, X.size))
    points[:2,:] = np.array([X.ravel(), Y.ravel()])
    pointsback = hom2cart(np.dot(la.inv(H), points))
    
    # X = pointsback[0,:].reshape(X.shape) - in_region[0]
    # Y = pointsback[1,:].reshape(X.shape) - in_region[2]    
    # out = sample2D(img, [X, Y])
    
    # Warping with scipy's map_coordinates. It's a little faster,
    # but does not work with color images.
    shp = X.shape
    X = pointsback[0,:] - in_region[0]
    Y = pointsback[1,:] - in_region[2]
    out = np.empty((shp[0], shp[1], img.shape[2]), dtype=img.dtype)
    for i in range(img.shape[2]):
        out[:,:,i] = ndimage.map_coordinates(img[:,:,i], [Y,X], order=1).reshape(shp)
    out = np.squeeze(out)
    
    return out, out_region

def anaglyph(im1, im2):
    """Builds an anaglyph with two images."""
    color = im1.ndim > 2
    O = np.zeros((im1.shape[0], im1.shape[1], 3), dtype=im1.dtype)
    
    if color:
        O[:,:,0] = im1[:,:,0]
        O[:,:,1:] = im2[:,:,1:]
    else:
        O[:,:,0] = im1
        O[:,:,1] = im2
        O[:,:,2] = im2
    
    return O

def askpoints(image1, image2):
    """Ask for a list of point correspondences between two images."""
    
    points1 = []
    points2 = []
    
    # Prepare the two images.
    fig = ppl.gcf()
    fig.clf()
    ax1 = fig.add_subplot(121)
    ax1.imshow(image1)
    ax1.axis('image')
    ax2 = fig.add_subplot(122)
    ax2.imshow(image2)
    ax2.axis('image')
    ppl.draw()
    
    ax1.set_xlabel("Choose a point in left image (or right click to end)")
    p1 = ppl.ginput(1, timeout=-1, show_clicks=False, mouse_pop=2, mouse_stop=3)
    while len(p1) != 0:
        p1 = p1[0]
        ax1.plot(p1[0], p1[1], '.r')
        ax1.set_xlabel('')
        ax2.set_xlabel("Choose the matching point in right image")
        
        p2 = ppl.ginput(1, timeout=-1, show_clicks=False, mouse_pop=2, mouse_stop=3)
        if len(p2) == 0:
            break
        p2 = p2[0]
        ax2.plot(p2[0], p2[1], '.r')
        
        points1.append(p1)
        points2.append(p2)
        
        ax2.set_xlabel('')
        ax1.set_xlabel("Choose a point in left image (or right click to end)")
        p1 = ppl.ginput(1, timeout=-1, show_clicks=False, mouse_pop=2, mouse_stop=3)
    
    ax1.set_xlabel('')
    ax2.set_xlabel('')
    ppl.draw()
    
    # pdb.set_trace()

    # swap point co-ordinates
    
    num_points = len(points1)
    points1 = np.vstack((np.array(points1).T[:,:],np.ones(num_points)))
    points2 = np.vstack((np.array(points2).T[:,:],np.ones(num_points)))
    return points1, points2

def dense_reconstruction(S, P1, P2, H1, H2, region=None, step=1, imbw1=None):
    """
    Build and show a dense reconstruction.
    
    Parameters
    ----------
    S : ndarray
        Matrix of disparities.
    P1, P2 : ndarray
        Projection matrices of the stereo pair.
    H1, H2 : ndarray
        Homographies which rectify the images of the stereo
        pair. See projmat2rectify.
    region : array-like, optional
        Region of the matrix of disparities that will be used for
        the dense reconstruction. It must be expressed
        as [x_min, x_max, y_min, y_max].
        
        If not given, the full matrix of disparities is considered.
    step : integer, optional
        Quality of the reconstruction. Only one of every 'step' pixels
        inside the region of interest is taken for the reconstruction.
        
        If not given, all pixels are used.
    imbw1 : ndarray, optional
        The image before rectification. This is used to assign a color
        to the 3D vertices of the reconstruction. If not given, an arbitrary
        color is assigned to vertices.
        
        imbw1 should be a gray scale image.
    """
    if region is None:
        region = [0, S.shape[1], 0, S.shape[0]]
    
    # The matrix of disparities is smoothed.
    H = np.ones((3,3))/9.0
    S = ndimage.convolve(np.double(S), H, mode='constant')
    
    # Point correspondences.
    X, Y = np.mgrid[region[0]:region[1]+1:step, region[2]:region[3]+1:step]
    num_points = np.prod(X.shape)
    points1 = np.ones((3, num_points))
    points1[0,:] = X.ravel()
    points1[1,:] = Y.ravel()
    X2 = X.ravel() + S[np.int32(points1[1,:]), np.int32(points1[0,:])]
    points2 = np.copy(points1)
    points2[0,:] = X2
    
    # Colors
    if imbw1 is not None:
        points1back = hom2cart(np.dot(la.inv(H1), points1))
        colors = ndimage.map_coordinates(imbw1, [points1back[1], points1back[0]], order=1)
    else:
        colors = None
    
    # Polygons.
    vlist = np.arange(0, num_points)
    vlist = vlist.reshape(X.shape)
    vlist1 = vlist[:-1, :-1]
    vlist2 = vlist[:-1, 1:]
    vlist3 = vlist[1:, 1:]
    vlist4 = vlist[1:, :-1]
    faces1 = np.array([vlist1.ravel(), vlist2.ravel(), vlist3.ravel()])
    faces2 = np.array([vlist1.ravel(), vlist3.ravel(), vlist4.ravel()])
    faces = matarray(faces1, faces2).T
    
    # Reconstruction.
    #    from stereo import reconstruct
    M = reconstruct(points1, points2, np.dot(H1, P1), np.dot(H2, P2))
    
    # Show the result.
    try:
        from enthought.mayavi import mlab
    except ImportError:
        from mayavi import mlab
    mlab.clf()
    mlab.triangular_mesh(M[0], M[1], M[2], faces, scalars=colors, colormap='gray')
    
    return M, faces, colors

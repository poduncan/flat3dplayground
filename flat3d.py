import numpy as np
import gizeh as gz
import cairocffi as cr
import moviepy.editor as mpy

class Element2d(object):
	def __init__(self):
		pass
	def isPolygon(self):
		return False
	def isPolyline(self):
		return False
	def isDot(self):
		return False

class Polygon2d(Element2d):
	def __init__(self, points, fill=None):
		super(Polygon2d, self).__init__()
		self.points = points
		self.fill = fill
	def isPolygon(self):
		return True

class Polyline2d(Element2d):
	def __init__(self, points, stroke=None, width=None, closed=False, capbutt=False):
		super(Polyline2d, self).__init__()
		self.points = points
		self.stroke = stroke
		self.width = width
		self.closed = closed
		self.capbutt = capbutt
	def isPolyline(self):
		return True

class Dot2d(Element2d):
	def __init__(self, point, stroke=None, width=None):
		super(Dot2d, self).__init__()
		self.point = point
		self.stroke = stroke
		self.width = width
	def isDot(self):
		return True

class SurfaceAliased(gz.Surface, object):
	def __init__(self, scale, width, height):
		super(SurfaceAliased, self).__init__(width=width, height=height)
		self.scale = scale;
	def get_new_context(self):
		cxt = super(SurfaceAliased, self).get_new_context()
		cxt.set_antialias(cr.ANTIALIAS_NONE)
		return cxt

def XFscale2d(x, y=None):
	if (y is None):
		y = x
	return [[x, 0, 0],
	        [0, y, 0],
	        [0, 0, 1]]

def XFtranslate2d(x, y):
	return [[1, 0, x],
	        [0, 1, y],
	        [0, 0, 1]]

def XFrotate2d(a):
	return [[ np.cos(a), -np.sin(a), 0],
	        [ np.sin(a),  np.cos(a), 0],
	        [         0,          0, 1]]

def rad(a):
	return np.deg2rad(a)

def XFscale3d(x, y=None, z=None):
	if (y is None):
		y = x
		if (z is None):
			z = x
	elif (z is None):
		z = 1
	return [[x, 0, 0, 0],
	        [0, y, 0, 0],
	        [0, 0, z, 0],
	        [0, 0, 0, 1]]

def XFtranslate3d(x, y, z):
	return [[1, 0, 0, x],
	        [0, 1, 0, y],
	        [0, 0, 1, z],
	        [0, 0, 0, 1]]

def XFrotateX3d(a):
	return [[         1,          0,          0, 0],
	        [         0,  np.cos(a), -np.sin(a), 0],
	        [         0,  np.sin(a),  np.cos(a), 0],
	        [         0,          0,          0, 1]]

def XFrotateY3d(a):
	return [[ np.cos(a),          0,  np.sin(a), 0],
	        [         0,          1,          0, 0],
	        [-np.sin(a),          0,  np.cos(a), 0],
	        [         0,          0,          0, 1]]

def XFrotateZ3d(a):
	return [[ np.cos(a), -np.sin(a),          0, 0],
	        [ np.sin(a),  np.cos(a),          0, 0],
	        [         0,          0,          0, 0],
	        [         0,          0,          0, 1]]

class Scene2d(object):
	def __init__(self, w, h, scale=1, transform=np.identity(3)):
		self.w = scale*w
		self.h = scale*h
		self.elements = []
		self.scale = scale
		self.transform = transform
	def addElem(self, elem):
		if (not (elem.isPolygon() or elem.isPolyline() or elem.isDot())):
			raise TypeError("cannot add element to scene")
		self.elements.append(elem)
	def get_gizeh_surface(self):
		surface = SurfaceAliased(scale=self.scale, width=int(self.w), height=int(self.h))
		tf = np.matmul(XFscale2d(self.scale), self.transform)
		for elem in self.elements:
			if (elem.isPolygon()):
				points = list(map(lambda x: np.matmul(tf, [x[0], x[1], 1])[:2], elem.points))
				polygon = gz.polyline(points, fill=elem.fill, close_path=True)
				polygon.draw(surface)
			elif (elem.isPolyline()):
				points = list(map(lambda x: np.matmul(tf, [x[0], x[1], 1])[:2], elem.points))
				polyline = gz.polyline(points, stroke=elem.stroke, stroke_width=self.scale*elem.width, close_path=elem.closed, line_cap=('butt' if elem.capbutt else 'round'))
				polyline.draw(surface)
			elif (elem.isDot()):
				x = elem.point
				dot = gz.circle(r=self.scale*elem.width/2.0, xy=np.matmul(tf, [x[0], x[1], 1])[:2], fill=elem.stroke)
				dot.draw(surface)
			else:
				raise TypeError("cannot make gizeh element")
		return surface

def export_vid(name, make_surface, duration, fps=24):
	t_prev = [-1.0]
	im = [None]

	scale = make_surface(0).scale

	def update(t):
		if (t != t_prev[0]):
			surface = make_surface(t)
			im[0] = surface.get_npimage(transparent=True)
			t_prev[0] = t

	def make_frame(t):
		update(t)
		return im[0][:,:,:3]

	def make_mask(t):
		update(t)
		return im[0][:,:,3]/255.0

	mask = mpy.VideoClip(make_mask, duration=duration, ismask=True).resize(1.0/scale)
	clip = mpy.VideoClip(make_frame, duration=duration).set_mask(mask).resize(1.0/scale)
	clip.write_videofile("%s.mov" % name, fps=fps, codec='png', with_mask=True)

def export_img(name, surface):
	filename = "%s.png" % name
	surface.write_to_png(filename)
	print "[flat3D]", "Image ready:", filename

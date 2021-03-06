import numpy as np
import gizeh as gz
import cairocffi as cr
import moviepy.editor as mpy
import xform as xf
import copy

class Scene(object):
	def __init__(self):
		pass

class Clipper(object):
	def __init__(self):
		pass
	def contains(self, point):
		return True
	def intersect(self, pa, pb):
		return None
	def intersect(self, pa, pb, paw=1, pbw=1):
		return None
	def isLineClipper(self):
		return False
	def isTruthClipper(self):
		return False

class TrueClipper(Clipper):
	def __init__(self):
		super(Clipper, self).__init__()
	def contains(self, point):
		return True
	def intersect(self, pa, pb, paw=1, pbw=1):
		raise TypeError("intersecting with TrueClipper")
	def isTruthClipper(self):
		return True

class LineClipper(Clipper):
	def __init__(self, linepnt, linedir):
		super(Clipper, self).__init__()
		self.linepnt = linepnt
		self.linedir = linedir
	def contains(self, point):
		topoint = (point[0] - self.linepnt[0], point[1] - self.linepnt[1])
		return 0 >= self.linedir[0]*topoint[1] - topoint[0]*self.linedir[1]
	def intersect(self, pa, pb, paw=1, pbw=1):
		tob = (pb[0] - pa[0], pb[1] - pa[1])
		tobw = pbw - paw
		t = (self.linedir[0]*(pa[1] - self.linepnt[1]) - self.linedir[1]*(pa[0] - self.linepnt[0])) / (self.linedir[1]*tob[0] - self.linedir[0]*tob[1])
		return (pa[0] + t*tob[0], pa[1] + t*tob[1]), paw + t*tobw
	def isLineClipper(self):
		return True

class InverseClipper(Clipper):
	def __init__(self, inv):
		super(Clipper, self).__init__()
		self.inv = inv
	def contains(self, point):
		return not self.inv.contains(point)
	def intersect(self, pa, pb, paw=1, pbw=1):
		return self.inv.intersect(pa, pb, paw, pbw)
	def isLineClipper(self):
		return self.inv.isLineClipper()
	def isTruthClipper(self):
		return self.inv.isTruthClipper()

class Element2d(object):
	def __init__(self):
		pass
	def tf(self, tf):
		pass
	def clip(self, clipper):
		pass
	def isClipped(self):
		return False
	def perspectivize(self, fov, aspect):
		pass
	def isPolygon(self):
		return False
	def isPolyline(self):
		return False
	def isDot(self):
		return False
	def isText(self):
		return False

class Polygon2d(Element2d):
	def __init__(self, points, w_s=None, fill=None):
		super(Polygon2d, self).__init__()
		self.points = points
		if (w_s is None):
			self.w_s = np.ones(len(points))
		elif (len(w_s) == len(points)):
			self.w_s = w_s
		else:
			raise TypeError("different number of points and w_s")
		if (fill is None):
			self.fill = (1,0,0)
		else:
			self.fill = fill
	def tf(self, tf):
		self.points = list(map(lambda x: xf.m(tf,x), self.points))
		return self
	def clip(self, clipper):
		if (clipper.isLineClipper()):
			if (len(self.points) > 0):
				newpoints = []
				newWs = []
				S = self.points[-1]
				Sw = self.w_s[-1]
				for i in range(len(self.points)):
					E = self.points[i]
					Ew = self.w_s[i]
					if (clipper.contains(E)):
						if (not clipper.contains(S)):
							pt, w = clipper.intersect(S, E, Sw, Ew)
							if np.isfinite(pt[0]) and np.isfinite(pt[1]) and np.isfinite(w):
								newpoints.append(pt)
								newWs.append(w)
						newpoints.append(E)
						newWs.append(Ew)
					elif (clipper.contains(S)):
						pt, w = clipper.intersect(S, E, Sw, Ew)
						if np.isfinite(pt[0]) and np.isfinite(pt[1]) and np.isfinite(w):
							newpoints.append(pt)
							newWs.append(w)
					S = E
					Sw = Ew
				self.points = newpoints
				self.w_s = newWs
		elif (clipper.isTruthClipper()):
			if (not clipper.contains((0,0))):
				self.points = []
				self.w_s = []
		else:
			raise TypeError("unrecognized clipper")
		return self
	def isClipped(self):
		return len(self.points) == 0
	def perspectivize(self, fov, aspect):
		for i in range(len(self.points)):
			self.points[i] = xf.m(xf.scale2d(1.0/(self.w_s[i] * np.tan(fov/2.0) * aspect), 1.0/(self.w_s[i] * np.tan(fov/2.0))), self.points[i])
	def isPolygon(self):
		return True

class Polyline2d(Element2d):
	def __init__(self, points, w_s=None, stroke=None, width=None, closed=False, capbutt=False):
		super(Polyline2d, self).__init__()
		self.points = points
		if (w_s is None):
			self.w_s = np.ones(len(points))
		elif (len(w_s) == len(points)):
			self.w_s = w_s
		else:
			raise TypeError("different number of points and w_s")
		if (stroke is None):
			self.stroke = (0,1,0)
		else:
			self.stroke = stroke
		if (width is None):
			self.width = 2
		else:
			self.width = width
		self.closed = closed
		self.capbutt = capbutt
	def tf(self, tf):
		self.points = list(map(lambda x: xf.m(tf,x), self.points))
		return self
	def clip(self, clipper):
		if (clipper.isLineClipper()):
			# note: only works with single lines
			if (len(self.points) > 0):
				newpoints = []
				newWs = []
				S = self.points[-1]
				Sw = self.w_s[-1]
				for i in range(len(self.points)):
					E = self.points[i]
					Ew = self.w_s[i]
					if (clipper.contains(E)):
						if (not clipper.contains(S)):
							pt, w = clipper.intersect(S, E, Sw, Ew)
							if np.isfinite(pt[0]) and np.isfinite(pt[1]) and np.isfinite(w):
								newpoints.append(pt)
								newWs.append(w)
						newpoints.append(E)
						newWs.append(Ew)
					elif (clipper.contains(S)):
						pt, w = clipper.intersect(S, E, Sw, Ew)
						if np.isfinite(pt[0]) and np.isfinite(pt[1]) and np.isfinite(w):
							newpoints.append(pt)
							newWs.append(w)
					S = E
					Sw = Ew
				self.points = newpoints
				self.w_s = newWs
		elif (clipper.isTruthClipper()):
			if (not clipper.contains((0,0))):
				self.points = []
				self.w_s = []
		else:
			raise TypeError("unrecognized clipper")
		return self
	def isClipped(self):
		return len(self.points) == 0
	def perspectivize(self, fov, aspect):
		for i in range(len(self.points)):
			self.points[i] = xf.m(xf.scale2d(1.0/(self.w_s[i] * np.tan(fov/2.0) * aspect), 1.0/(self.w_s[i] * np.tan(fov/2.0))), self.points[i])
	def isPolyline(self):
		return True

class Dot2d(Element2d):
	def __init__(self, point, w=1, stroke=None, width=None):
		super(Dot2d, self).__init__()
		self.point = point
		self.w = w
		if (stroke is None):
			self.stroke = (1,1,0)
		else:
			self.stroke = stroke
		if (width is None):
			self.width = 2
		else:
			self.width = width
		self.clipped = False
	def tf(self, tf):
		self.point = xf.m(tf, self.point)
		return self
	def clip(self, clipper):
		if (not clipper.contains(self.point)):
			self.clipped = True
		return self
	def isClipped(self):
		return self.clipped
	def perspectivize(self, fov, aspect):
		self.point = xf.m(xf.scale2d(1.0/(self.w * np.tan(fov/2.0) * aspect), 1.0/(self.w * np.tan(fov/2.0))), self.point)
	def isDot(self):
		return True

class Text2d(Element2d):
	def __init__(self, position, fill, txt, fontfamily, fontsize, bold=False, v_align="center", h_align="center"):
		super(Text2d, self).__init__()
		self.position = position
		self.fill = fill
		self.txt = txt
		self.fontfamily = fontfamily
		self.fontsize = fontsize
		self.fill = fill
		self.bold = bold
		self.v_align = v_align
		self.h_align = h_align
	def tf(self, tf):
		self.position = xf.m(tf, self.position)
		return self
	def isClipped(self):
		return False
	def isText(self):
		return True

class SurfaceAliased(gz.Surface, object):
	def __init__(self, scale, width, height):
		super(SurfaceAliased, self).__init__(width=width, height=height)
		self.scale = scale;
	def get_new_context(self):
		cxt = super(SurfaceAliased, self).get_new_context()
		cxt.set_antialias(cr.ANTIALIAS_NONE)
		return cxt

class Scene2d(Scene):
	def __init__(self, w, h, scale=1, transform=np.identity(3)):
		super(Scene2d, self).__init__()
		self.w = scale*w
		self.h = scale*h
		self.elements = []
		self.scale = scale
		self.transform = transform
	def addElem(self, elem):
		if (not (elem.isPolygon() or elem.isPolyline() or elem.isDot() or elem.isText())):
			raise TypeError("cannot add element to scene")
		self.elements.append(elem)
	def get_gizeh_surface(self):
		surface = SurfaceAliased(scale=self.scale, width=int(self.w), height=int(self.h))
		tf = np.matmul(xf.scale2d(self.scale), self.transform)
		for elem in self.elements:
			elem.tf(tf)
			gzelem = None
			if (not elem.isClipped()):
				if (elem.isPolygon()):
					gzelem = gz.polyline(elem.points, fill=elem.fill, close_path=True)
				elif (elem.isPolyline()):
					gzelem = gz.polyline(elem.points, stroke=elem.stroke, stroke_width=self.scale*elem.width, close_path=elem.closed, line_cap=('butt' if elem.capbutt else 'round'))
				elif (elem.isDot()):
					gzelem = gz.circle(r=self.scale*elem.width/2.0, xy=elem.point, fill=elem.stroke)
				elif (elem.isText()):
					gzelem = gz.text(xy=elem.position, fill=elem.fill, txt=elem.txt, fontfamily=elem.fontfamily, fontsize=self.scale*elem.fontsize, fontweight=("bold" if elem.bold else "normal"), v_align=elem.v_align, h_align=elem.h_align)
				else:
					raise TypeError("cannot make gizeh element")
			if (not (gzelem is None)):
				gzelem.draw(surface)
		return surface

class Element3d(object):
	def __init__(self):
		pass
	def tf(self, tf):
		pass
	def isTriangle(self):
		return False
	def isLine(self):
		return False
	def isDot(self):
		return False

class Triangle3d(Element3d):
	def __init__(self, points, fill=None):
		super(Triangle3d, self).__init__()
		if (len(points) != 3):
			raise ValueError("3D Triangles need 3 points, but %d were given" % len(points))
		self.points = points
		self.fill = fill
	def tf(self, tf):
		self.points = list(map(lambda x: xf.m(tf,x), self.points))
		return self
	def isTriangle(self):
		return True

class Line3d(Element3d):
	def __init__(self, points, stroke=None, width=None):
		super(Line3d, self).__init__()
		if (len(points) != 2):
			raise ValueError("3D Lines need 2 points, but %d were given" % len(points))
		self.points = points
		self.stroke = stroke
		self.width = width
	def tf(self, tf):
		self.points = list(map(lambda x: xf.m(tf,x), self.points))
		return self
	def isLine(self):
		return True

class Dot3d(Element3d):
	def __init__(self, point, stroke=None, width=None):
		super(Dot3d, self).__init__()
		self.point = point
		self.stroke = stroke
		self.width = width
	def tf(self, tf):
		self.point = xf.m(tf, self.point)
		return self
	def isDot(self):
		return True

class Camera3d(object):
	def __init__(self, position, direction, up, fov, aspect, near):
		self.position = position
		self.direction = direction
		self.up = up
		self.fov = fov
		self.aspect = aspect
		self.near = near

class Tree(object):
	def __init__(self, data=None, left=None, right=None):
		self.data = data
		self.left = left
		self.right = right
	def printTree(self, depth=0):
		print "\t"*depth + str(self.data)
		if (not self.left is None):
			print "left:"
			self.left.printTree(depth=depth+1)
		if (not self.right is None):
			print "right:"
			self.right.printTree(depth=depth+1)

class GeoNode(object):
	def __init__(self, elem, plane):
		self.elem = elem
		self.plane = plane
	def hasGeometry(self):
		if (self.elem.isPolygon()):
			return len(self.elem.points) > 0
		elif (self.elem.isPolyline()):
			return len(self.elem.points) > 0
		elif (self.elem.isDot()):
			return not self.elem.clipped
		else:
			raise TypeError("not 2D element")
	# !!! REMOVE THIS
	def __str__(self):
		return str(self.elem.fill)

class Scene3d(Scene):
	def __init__(self, w2d, h2d, scale2d=1, transform=np.identity(4), camera=None):
		super(Scene3d, self).__init__()
		self.w2d = w2d
		self.h2d = h2d
		self.scale2d = scale2d
		self.transform = transform
		self.elements = []
		self.camera = camera
	def addElem(self, elem):
		if (not (elem.isTriangle() or elem.isLine() or elem.isDot())):
			raise TypeError("cannot add element to scene")
		self.elements.append(elem)
	def geonodeFromElem3d(self, elem3d):
		# convert elem3d to elem2d (with smart zs) and plane (GeoNode)
		plane = None
		elem = None
		if (elem3d.isTriangle()):
			plane = xf.Plane(elem3d.points[0],
			                      xf.cross((elem3d.points[1][0] - elem3d.points[0][0], elem3d.points[1][1] - elem3d.points[0][1], elem3d.points[1][2] - elem3d.points[0][2]),
			                   	           (elem3d.points[2][0] - elem3d.points[0][0], elem3d.points[2][1] - elem3d.points[0][1], elem3d.points[2][2] - elem3d.points[0][2])))
			elem = Polygon2d([(elem3d.points[0][0], elem3d.points[0][1]), (elem3d.points[1][0], elem3d.points[1][1]), (elem3d.points[2][0], elem3d.points[2][1])],
				                   w_s=[-elem3d.points[0][2], -elem3d.points[1][2], -elem3d.points[2][2]],
				                   fill=elem3d.fill)
		elif (elem3d.isLine()):
			linedir = (elem3d.points[1][0] - elem3d.points[0][0], elem3d.points[1][1] - elem3d.points[0][1], elem3d.points[1][2] - elem3d.points[0][2])
			zaxis = (0, 0, 1)
			plane = xf.Plane(elem3d.points[0],
			                      xf.cross(xf.cross(linedir, zaxis), linedir))
			elem = Polyline2d([(elem3d.points[0][0], elem3d.points[0][1]), (elem3d.points[1][0], elem3d.points[1][1])],
				                   w_s=[-elem3d.points[0][2], -elem3d.points[1][2]],
			                       stroke=elem3d.stroke, width=elem3d.width)
		elif (elem3d.isDot()):
			plane = xf.Plane(elem3d.point, (0, 0, 1))
			elem = Dot2d((elem3d.point[0], elem3d.point[1]), w=-elem3d.point[2], stroke=elem3d.stroke, width=elem3d.width)
		else:
			raise TypeError("not 3D element")

		# intersect with near plane
		nppt = (0, 0, -self.camera.near)
		npnm = (0, 0, 1)
		lineClipperDirection = xf.cross(npnm, plane.nm)
		if (xf.length3d(lineClipperDirection) < 1e-10):
			# elem is directy facing camera
			if (plane.pt[2] > -self.camera.near):
				# elem is entirely in from of near plane
				elem.clip(InverseClipper(TrueClipper()))
		else:
			lineClipperDirection = xf.norm3d(lineClipperDirection)
			# solve for point on both planes and make lineclipper (can use line-plane intersection)
			proj = (plane.nm[0], plane.nm[1], 0)
			lineClipperPoint = self.intersectLinePlane(nppt, proj, plane.pt, plane.nm)

			lineClipper = LineClipper(lineClipperPoint, lineClipperDirection)

			if (plane.nm[2] <= 0):
				lineClipper = InverseClipper(lineClipper)

			elem.clip(lineClipper)

		if (elem.isClipped()):
			return None

		elem.perspectivize(self.camera.fov, self.camera.aspect)

		return GeoNode(elem=elem, plane=plane)
	def intersectLinePlane(self, linepnt, linedir, planept, planenm):
		if (xf.dot3d(linedir, planenm)**2 < 1e-10):
			# parallel
			return None
		t = xf.dot3d(planenm, (planept[0] - linepnt[0], planept[1] - linepnt[1], planept[2] - linepnt[2])) / xf.dot3d(planenm, linedir)
		return (linepnt[0] + t*linedir[0], linepnt[1] + t*linedir[1], linepnt[2] + t*linedir[2])
	def insertToTree(self, tree, geonode):
		if (geonode is None):
			return

		# if tree is None, make tree with this geonode
		if (tree.data is None):
			tree.data = geonode
		else:

			# clip according to tree's GeoNode
			frontClipper = None
			backClipper = None
			lineClipperDirection = xf.cross(tree.data.plane.nm, geonode.plane.nm)
			if (xf.length3d(lineClipperDirection) < 1e-10):
				# planes are parallel
				# do line-plane intersection to determine closer plane
				# planept is a point on the geonode plane that is directly "above" or "below" the tree.data plane point
				planept = self.intersectLinePlane(tree.data.plane.pt, tree.data.plane.nm, geonode.plane.pt, geonode.plane.nm)
				toPlanept = (planept[0] - self.camera.position[0], planept[1] - self.camera.position[1], planept[2] - self.camera.position[2])
				toGeopt = (tree.data.plane.pt[0] - self.camera.position[0], tree.data.plane.pt[1] - self.camera.position[1], tree.data.plane.pt[2] - self.camera.position[2])
				if (xf.length3d(toPlanept) < xf.length3d(toGeopt)):
					frontClipper = TrueClipper()
					backClipper = InverseClipper(frontClipper)
				else:
					backClipper = TrueClipper()
					frontClipper = InverseClipper(backClipper)
				# set either front or back clipper to trueclipper
			else:
				lineClipperDirection = xf.norm3d(lineClipperDirection)
				# solve for point on both planes and make lineclipper (can use line-plane intersection)
				templen = xf.dot3d(tree.data.plane.nm, geonode.plane.nm) / (xf.length3d(tree.data.plane.nm)**2)
				proj = (geonode.plane.nm[0] - templen*tree.data.plane.nm[0], geonode.plane.nm[1] - templen*tree.data.plane.nm[1], geonode.plane.nm[2] - templen*tree.data.plane.nm[2])
				lineClipperPoint = self.intersectLinePlane(tree.data.plane.pt, proj, geonode.plane.pt, geonode.plane.nm)

				if (lineClipperPoint[2] > -self.camera.near):
					lineClipperPoint = self.intersectLinePlane(lineClipperPoint, lineClipperDirection, (0, 0, -1-self.camera.near), (0, 0, 1))

				if (lineClipperPoint[2] + lineClipperDirection[2] > -self.camera.near):
					intersectionPoint = self.intersectLinePlane(lineClipperPoint, lineClipperDirection, (0, 0, -1-self.camera.near), (0, 0, 1))
					lineClipperPoint = (intersectionPoint[0] - lineClipperDirection[0], intersectionPoint[1] - lineClipperDirection[1], intersectionPoint[2] - lineClipperDirection[2])

				plineClipperPoint = (lineClipperPoint[0] / (-lineClipperPoint[2] * np.tan(self.camera.fov/2.0) * self.camera.aspect), lineClipperPoint[1] / (-lineClipperPoint[2] * np.tan(self.camera.fov/2.0)))

				lineClipperPointPrime = (lineClipperPoint[0] + lineClipperDirection[0], lineClipperPoint[1] + lineClipperDirection[1], lineClipperPoint[2] + lineClipperDirection[2])
				plineClipperPointPrime = (lineClipperPointPrime[0] / (-lineClipperPointPrime[2] * np.tan(self.camera.fov/2.0) * self.camera.aspect), lineClipperPointPrime[1] / (-lineClipperPointPrime[2] * np.tan(self.camera.fov/2.0)))
				plineClipperDirection = (plineClipperPointPrime[0] - plineClipperPoint[0], plineClipperPointPrime[1] - plineClipperPoint[1])

				lineClipper = LineClipper(plineClipperPoint, plineClipperDirection)

				if (xf.dot3d(tree.data.plane.nm, tree.data.plane.pt) > 0) == (xf.dot3d(geonode.plane.nm, geonode.plane.pt) > 0):
					# lineclipper is back
					backClipper = lineClipper
					frontClipper = InverseClipper(backClipper)
				else:
					# lineclipper is front
					frontClipper = lineClipper
					backClipper = InverseClipper(frontClipper)

			backGeoNode = GeoNode(elem=copy.deepcopy(geonode.elem).clip(backClipper), plane=geonode.plane)
			if (not backGeoNode.elem.isClipped()):
				if (tree.left is None):
					tree.left = Tree(data=backGeoNode)
				else:
					self.insertToTree(tree.left, backGeoNode)

			frontGeoNode = GeoNode(elem=copy.deepcopy(geonode.elem).clip(frontClipper), plane=geonode.plane)

			if (not frontGeoNode.elem.isClipped()):
				if (tree.right is None):
					tree.right = Tree(data=frontGeoNode)
				else:
					self.insertToTree(tree.right, frontGeoNode)

	def drawTree(self, scene2d, tree):
		if (not tree.left is None):
			self.drawTree(scene2d, tree.left)

		if (not tree.data is None):
			scene2d.addElem(tree.data.elem)

		if (not tree.right is None):
			self.drawTree(scene2d, tree.right)
	def get_gizeh_surface(self):
		tf = self.transform
		v_x = xf.norm3d(xf.cross(self.camera.direction, self.camera.up))
		v_y = xf.norm3d(xf.cross(v_x, self.camera.direction))
		v_z = xf.norm3d(xf.cross(v_x, v_y))
		v_r_inv = [[v_x[0], v_y[0], v_z[0], 0],
		           [v_x[1], v_y[1], v_z[1], 0],
		           [v_x[2], v_y[2], v_z[2], 0],
		           [     0,      0,      0, 1]]
		v = xf.M(np.linalg.inv(v_r_inv), xf.translate3d(-self.camera.position[0], -self.camera.position[1], -self.camera.position[2]))
		scene2d = Scene2d(w=self.w2d, h=self.h2d, scale=self.scale2d, transform=xf.M(xf.translate2d(self.w2d/2.0, self.h2d/2.0), xf.scale2d(self.w2d/2.0, -self.h2d/2.0)))
		
		# make tree
		tree = Tree()
		for elem in self.elements:
			elem.tf(tf)
			elem.tf(v)
			self.insertToTree(tree, self.geonodeFromElem3d(elem))

		# tree.printTree()
		# TODO apply perspective via w parameter in 2d elements

		# make scene2d via in-order traversal of tree
		self.drawTree(scene2d, tree)

		return scene2d.get_gizeh_surface()


def export_vid(name, make_scene, duration, fps=24):
	t_prev = [-1.0]
	im = [None]

	def make_surface(t):
		return make_scene(t).get_gizeh_surface()

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

def export_img(name, scene):
	surface = scene.get_gizeh_surface()
	filename = "%s.png" % name
	surface.write_to_png(filename)
	print "[flat3D]", "Image ready:", filename

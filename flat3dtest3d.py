import flat3d as f3d
import xform as xf
import numpy as np

W = 1920.0
H = 1080.0
duration = 4

# scale = 1.0/4
scale = 1.0
# scale = 4.0

def makescene(t):
	dist = 5
	camera = f3d.Camera3d(position=(dist*np.sin(t*np.pi/2.0),-dist*np.cos(t*np.pi/2.0),0), direction=(-np.sin(t*np.pi/2.0),np.cos(t*np.pi/2.0),0), up=(0,0,1), fov=xf.rad(60), aspect=W/H, near=1e-6)
	# camera = f3d.Camera3d(position=(0,-4 + 1.5*t,0), direction=(0,1,0), up=(0,0,1), fov=xf.rad(60), aspect=W/H, near=1e-2)
	
	scene = f3d.Scene3d(w2d=W, h2d=H, scale2d=scale, camera=camera)

	# scene.addElem(f3d.Line3d(points=[(-0.5,0.25,-0.6), (0.5,2,1)], stroke=(0,1,1), width=5))
	# scene.addElem(f3d.Triangle3d(points=[(-1,1,-0.5), (1*t + 0*(1-t), 1*t + 0.25*(1-t), 0*t + -1*(1-t)), (0,1,1)], fill=(1,1,0)))
	# scene.addElem(f3d.Dot3d(point=(-0.5,2*t,0.5), stroke=(0,1,1), width=5))
	# scene.addElem(f3d.Triangle3d(points=[(-1,2,1), (0,0,-1), (1,1,0.5)], fill=(1,0,0)))

	# scene.addElem(f3d.Triangle3d(points=[(-1,5*t+0.25,0), (1,5*t+0.25,0), (0,5*t+0.25,1)], fill=(0,1,1)))
	# scene.addElem(f3d.Triangle3d(points=[(-1,5*t+0.5,-0.5), (1,5*t+0.5,0), (0,5*t+0.5,1)], fill=(1,1,0)))

	# scene.addElem(f3d.Triangle3d(points=[(-1,5*t+0.25,0), (1,5*t+0.25,0), (0,5*t+0.25,1)], fill=(0,1,1)))
	# scene.addElem(f3d.Triangle3d(points=[(-1,5*t+0.5,-0.5), (1,5*t+0.5,0), (0,5*t+0.5,1)], fill=(1,1,0)))
	# scene.addElem(f3d.Triangle3d(points=[(-1,1,0), (1,1,0), (0,1,1)], fill=(1,1,1)))
	
	scene.addElem(f3d.Triangle3d(points=[(-1,2,1), (0,0,-1), (1,1,0.5)], fill=(1,0,0)))
	scene.addElem(f3d.Triangle3d(points=[(-1,1,-0.5), (1, 1, 0), (0,1,1)], fill=(1,1,0)))
	scene.addElem(f3d.Triangle3d(points=[(-0.5, 0.5, -0.25), (1, 1, -0.5), (-0.25, 1.5, 1)], fill=(0,1,0)))
	scene.addElem(f3d.Line3d(points=[(-1,-0.5,-1), (0.5,1.5,0.5)], stroke=(0.5,0,1), width=2))
	# scene.addElem(f3d.Line3d(points=[(0,0,0), (1,1,1)], stroke=(0,1,1), width=5))
	# scene.addElem(f3d.Triangle3d(points=[(0,0,0), (1,1,1), (1,1,0)], fill=(0,0.5,1)))
	scene.addElem(f3d.Dot3d(point=(-0.5, 0, 0.5), stroke=(1,1,1), width=5))
	
	return scene

f3d.export_vid('cool3dEffects', makescene, duration)
# f3d.export_img('cool3dEffects', makescene(0))
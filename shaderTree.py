from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.uix.scatter import Scatter
from kivy.properties import StringProperty, ObjectProperty
from kivy.graphics import RenderContext, Fbo, Color, Rectangle
from kivy.uix.boxlayout import BoxLayout


class ShaderWidget(FloatLayout):

	# property to set the source code for fragment shader
	fs = StringProperty(None)

	# texture of the framebuffer
	texturee = ObjectProperty(None)

	def __init__(self, **kwargs):
		# Instead of using canvas, we will use a RenderContext,
		# and change the default shader used.
		self.canvas = RenderContext(use_parent_projection=True)

		# We create a framebuffer at the size of the window
		# FIXME: this should be created at the size of the widget
		with self.canvas:
			self.fbo = Fbo(size=Window.size, use_parent_projection=True)

		# Set the fbo background to black.
		with self.fbo:
			Color(0, 0.5, 0)
			Rectangle(size=Window.size)

		# call the constructor of parent
		# if they are any graphics object, they will be added on our new canvas
		super(ShaderWidget, self).__init__(**kwargs)

		# We'll update our glsl variables in a clock
		Clock.schedule_interval(self.update_glsl, 0)

		# Don't forget to set the texture property to the texture of framebuffer
		self.texture = self.fbo.texture

	def update_glsl(self, *largs):
		self.canvas['time'] = Clock.get_boottime()
		self.canvas['resolution'] = [float(v) for v in self.size]

	def on_fs(self, instance, value):
		print("fs change",value)
		# set the fragment shader to our source code
		shader = self.canvas.shader
		old_value = shader.fs
		shader.fs = value
		if not shader.success:
			shader.fs = old_value
			raise Exception('failed')

	#
	# now, if we have new widget to add,
	# add their graphics canvas to our Framebuffer, not the usual canvas.
	#

	def add_widget(self, widget):
		c = self.canvas
		self.canvas = self.fbo
		super(ShaderWidget, self).add_widget(widget)
		self.canvas = c

	def remove_widget(self, widget):
		c = self.canvas
		self.canvas = self.fbo
		super(ShaderWidget, self).remove_widget(widget)
		self.canvas = c

###############################################################################
#             Character Controller | Template v 1.0 | UPBGE 0.2.3             #
###############################################################################
#                      Created by: Guilherme Teres Nunes                      #
#                       Access: youtube.com/UnidayStudio                      #
#                               github.com/UnidayStudio                       #
###############################################################################
# Character Controller Component:
#	Create a capsule for your character, set the physics type to "Character"
# and attach this Component to them.
# You can configure the Walk, Run speed and the Max Jumps on the Component
# panel. If your character object have Collision Bounds activated, I'd
# recommend to enable the "Avoid Sliding" option.
# 	If you want to make your character jump in a static direction, activate
# "Static Jump Direction". It means that, if the player wasn't moving when
# he pressed Space, the character will jump up and the player will not be able
# to change this during the jump. The same for when he was moving when pressed
# Space. Same for the rotation (Static Jump Rotation).
###############################################################################
import bge
from collections import OrderedDict
from mathutils import Vector, Matrix

def clamp(x, a, b):
	return min(max(a, x), b)

class CharacterController(bge.types.KX_PythonComponent):
	args = OrderedDict([
		("Activate"              , True),
		("Walk Speed"            , 0.1),
		("Run Speed"             , 0.2),
		("Max Jumps"             , 1),
		("Avoid Sliding"         , True),
		("Static Jump Direction" , False),
		("Static Jump Rotation"  , False),
		("Smooth Character Movement", 0.0),
		("Make Object Invisible" , False),
	])

	# Start Function
	def start(self, args):
		self.active = args["Activate"]

		self.walkSpeed = args["Walk Speed"]
		self.runSpeed  = args["Run Speed"]

		self.avoidSliding = args["Avoid Sliding"]
		self.__lastPosition = self.object.worldPosition.copy()
		self.__lastDirection = Vector([0,0,0])
		self.__smoothSlidingFlag = False

		self.__smoothMov  = clamp(args["Smooth Character Movement"], 0, 0.99)
		self.__smoothLast = Vector([0,0,0])

		self.staticJump = args["Static Jump Direction"]
		self.__jumpDirection = [0,0,0]

		self.staticJumpRot = args["Static Jump Rotation"]
		self.__jumpRotation = Matrix.Identity(3)

		self.character = bge.constraints.getCharacter(self.object)
		self.character.maxJumps = args["Max Jumps"]

		if self.active:
			if args["Make Object Invisible"]:
				self.object.visible = False

	# Makes the character walk with W,A,S,D (You can run by holding Left Shift)
	def characterMovement(self):
		keyboard = bge.logic.keyboard.inputs
		keyTAP = bge.logic.KX_INPUT_JUST_ACTIVATED

		x = 0; y = 0; speed = self.walkSpeed

		if keyboard[bge.events.LEFTSHIFTKEY].values[-1]:
			speed = self.runSpeed

		if keyboard[bge.events.WKEY].values[-1]:   y = 1
		elif keyboard[bge.events.SKEY].values[-1]: y = -1
		if keyboard[bge.events.AKEY].values[-1]:   x = -1
		elif keyboard[bge.events.DKEY].values[-1]: x = 1

		vec = Vector([x, y, 0])
		self.__smoothSlidingFlag = False
		if vec.length != 0:
			self.__smoothSlidingFlag = True
			# Normalizing the vector. For some reason, the mathutils normalize
			# don't work very well.
			vec /= vec.length
			# Multiply by the speed
			vec *= speed

		# This part is to make the static jump Direction works.
		if not self.character.onGround:
			if self.staticJump:
				vec = self.__jumpDirection
			if self.staticJumpRot:
				self.object.worldOrientation = self.__jumpRotation.copy()
		else:#elif self.character.onGround:
			self.__jumpDirection = vec
			self.__jumpRotation  = self.object.worldOrientation.copy()



		smooth = 1.0 - self.__smoothMov
		vec = self.__smoothLast.lerp(vec, smooth)
		self.__smoothLast = vec
		test = self.object.worldPosition.copy()
		self.character.walkDirection = self.object.worldOrientation * vec

		#if self.__smoothLast.length <= 0.001 and not self.__smoothSlidingFlag:
		#	self.__smoothLast = Vector([0,0,0])

		if vec.length != 0:
			self.__lastDirection = self.object.worldPosition - self.__lastPosition
			self.__lastPosition = self.object.worldPosition.copy()

	# Makes the Character jump with SPACE.
	def characterJump(self):
		keyboard = bge.logic.keyboard.inputs
		keyTAP = bge.logic.KX_INPUT_JUST_ACTIVATED

		if keyTAP in keyboard[bge.events.SPACEKEY].queue:
			self.character.jump()

	# Avoids the character to slide. This funtion is useful when you have
	# Collision Bounds activated.
	def avoidSlide(self):
		self.object.worldPosition[0] = self.__lastPosition[0]
		self.object.worldPosition[1] = self.__lastPosition[1]

		other = self.object.worldOrientation * self.__smoothLast

		if self.__lastDirection.length != 0 and other.length != 0:
			if self.__lastDirection.angle(other) > 0.5:
				if not self.__smoothSlidingFlag:
					self.__smoothLast = Vector([0,0,0])

	# Update Function
	def update(self):
		if self.active:
			self.characterMovement()
			self.characterJump()

			if self.avoidSliding:
				self.avoidSlide()


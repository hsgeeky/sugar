import goocanvas

from sugar.canvas.IconItem import IconItem
from sugar.canvas.IconColor import IconColor
from sugar.canvas.CanvasBox import CanvasBox
from sugar.presence import PresenceService
from view.BuddyIcon import BuddyIcon
from model.BuddyInfo import BuddyInfo
from view.frame.MenuStrategy import MenuStrategy

class RightPanel(CanvasBox):
	def __init__(self, shell):
		CanvasBox.__init__(self, shell.get_grid(), CanvasBox.VERTICAL, 1)
		self._shell = shell
		self._activity_ps = None
		self._joined_hid = -1
		self._left_hid = -1
		self._buddies = {}

		self._pservice = PresenceService.get_instance()
		self._pservice.connect('activity-appeared',
							   self.__activity_appeared_cb)

		shell.get_model().connect('activity-changed',
								  self.__activity_changed_cb)

	def add(self, buddy):
		icon = BuddyIcon(self._shell, BuddyInfo(buddy))
		icon.set_menu_strategy(MenuStrategy())
		self.set_constraints(icon, 3, 3)
		self.add_child(icon)

		self._buddies[buddy.get_name()] = icon

	def remove(self, buddy):
		i = self.find_child(self._buddies[buddy.get_name()])
		self.remove_child(i)

	def clear(self):
		while (self.get_n_children() > 0):
			self.remove_child(0)
		self._buddies = {}

	def __activity_appeared_cb(self, pservice, activity_ps):
		activity = self._shell.get_model().get_current_activity()
		if activity and activity_ps.get_id() == activity.get_id():
			self._set_activity_ps(activity_ps)

	def _set_activity_ps(self, activity_ps):
		if self._activity_ps == activity_ps:
			return

		if self._joined_hid > 0:
			self._activity_ps.disconnect(self._joined_hid)
			self._joined_hid = -1
		if self._left_hid > 0:
			self._activity_ps.disconnect(self._left_hid)
			self._left_hid = -1

		self._activity_ps = activity_ps

		self.clear()

		if activity_ps != None:
			for buddy in activity_ps.get_joined_buddies():
				self.add(buddy)

			self._joined_hid = activity_ps.connect(
							'buddy-joined', self.__buddy_joined_cb)
			self._left_hid = activity_ps.connect(
							'buddy-left', self.__buddy_left_cb)

	def __activity_changed_cb(self, group, activity):
		activity_ps = self._pservice.get_activity(activity.get_id())
		self._set_activity_ps(activity_ps)				

	def __buddy_joined_cb(self, activity, buddy):
		self.add(buddy)

	def __buddy_left_cb(self, activity, buddy):
		self.remove(buddy)

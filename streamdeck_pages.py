"""FreeCAD Stream Deck Addon - Stream Deck pages class
"""

## Modules
#


import re
from collections import namedtuple



## Classes
#

class StreamDeckPages():

  # Key and variable separators for page strings
  # Chosen to avoid clashing with any printable character used in the GUI
  # widgets
  SK = "\x1d"
  SV = "\x1e"

  # Named tuple for the 8 fields stored in each key string
  KeyFields = namedtuple("KeyFields",
    ["toolbar", "name", "enabled", "iconid", "toptext", "bottomtext", "left_brkt_clr", "right_brkt_clr"])

  def __init__(self, nb_streamdeck_keys, with_nav_keys):
    """__init__ method
    """

    self.nb_streamdeck_keys = nb_streamdeck_keys
    self.with_nav_keys = with_nav_keys

    self.previous_pages = []
    self.pages = []

    self.previous_current_page = None
    self.current_page = None
    self.current_page_no = None



  def parse_key(self, ks):
    """Parse a key string into its named fields."""
    return self.KeyFields(*ks.split(self.SV))



  def rebuild_pages(self, tbactions, repeated_toolbars,
			bracket_color_repeated_toolbars,
			bracket_color_page_nav_keys,
			brackets_color_expandable_tools):
    """Rebuild Stream Deck pages given a list of toolbars and actions passed as
    a ToolbarActions object
    """

    rep_brkt_clr = bracket_color_repeated_toolbars.lower()
    nav_brkt_clr = bracket_color_page_nav_keys.lower()
    exp_brkt_clr = brackets_color_expandable_tools.lower()

    empty_new_pages, last_empty_new_page_i = self._build_page_template(
        tbactions, repeated_toolbars, rep_brkt_clr, exp_brkt_clr)

    self._fill_toolbar_pages(tbactions, repeated_toolbars, empty_new_pages,
        last_empty_new_page_i, nav_brkt_clr, exp_brkt_clr)



  def _build_page_template(self, tbactions, repeated_toolbars,
				rep_brkt_clr, exp_brkt_clr):
    """Build one or more page templates that will be reused for each toolbar.

    Each template has the repeated toolbar keys pre-filled and contains
    [toolbar], [key], [pageprev] and [pagenext] placeholders for
    _fill_toolbar_pages to replace.

    Pages are SK-separated strings of SV-separated key fields:
      toolbar_marker SV name SV enabled SV iconid SV toptext SV bottomtext
        SV left_bracket_color SV right_bracket_color

    Returns (empty_new_pages, last_empty_new_page_i).
    """

    # Build the key strings for the repeated toolbars
    keys = []
    for t in repeated_toolbars:
      if t in tbactions.toolbars:
        last_action_i = len(tbactions.toolbar_actions[t]) - 1
        keys.extend(["[toolbar]{sv}{}{sv}{}{sv}{}{sv}{}{sv}{}{sv}{}{sv}{}".
		format(n, 1 if tbactions.actions[n].enabled else 0,
			tbactions.actions[n].iconid,
			tbactions.actions[n].title, t,
			rep_brkt_clr if i == 0 else \
			exp_brkt_clr if n in tbactions.expanded_actions else "",
			rep_brkt_clr if i == last_action_i else \
			exp_brkt_clr if not tbactions.expanded_actions.get(n, True) or \
				tbactions.actions[n].islastsubaction else "",
			sv = self.SV)
		for i, n in enumerate(tbactions.toolbar_actions[t])])
    nbkeys = len(keys)

    reserve_nb_last_keys = 2 if self.with_nav_keys else 0
    last_2_page_keys = "{sk}[pageprev]{sk}[pagenext]".format(sk = self.SK) \
                    if self.with_nav_keys else ""

    empty_new_pages = []

    # The last page of the new empty pages should have however many reserved
    # slots and at least 1 empty slot for a key left
    while nbkeys > self.nb_streamdeck_keys - reserve_nb_last_keys - 1:
      empty_new_pages.append(self.SK.join(keys[:self.nb_streamdeck_keys - \
						reserve_nb_last_keys]) + \
				last_2_page_keys)
      keys = keys[self.nb_streamdeck_keys - reserve_nb_last_keys:]
      nbkeys -= self.nb_streamdeck_keys - reserve_nb_last_keys

    empty_new_pages.append(self.SK.join(keys) + \
				(self.SK if keys and \
					(self.nb_streamdeck_keys - nbkeys - \
						reserve_nb_last_keys) \
					else "") + \
				self.SK.join(["[key]" for _ in \
					range(self.nb_streamdeck_keys - \
						nbkeys - \
						reserve_nb_last_keys)]) \
				+ last_2_page_keys)

    return empty_new_pages, len(empty_new_pages) - 1



  def _fill_toolbar_pages(self, tbactions, repeated_toolbars, empty_new_pages,
				last_empty_new_page_i, nav_brkt_clr, exp_brkt_clr):
    """Fill the page template with keys for each non-repeated toolbar,
    expanding [toolbar], [key], [pageprev] and [pagenext] placeholders as
    new pages are appended.
    Mutates self.pages.
    """

    self.previous_pages = self.pages
    self.pages = []
    prev_page_toolbar = None

    indiv_toolbar_page_maker_ctr = 0

    def page_marker():
      # Reads current t and counter on each call (intentional closure over loop vars)
      return "{}#{}".format(t, indiv_toolbar_page_maker_ctr)

    for t in tbactions.toolbars:
      if t not in repeated_toolbars:

        # Get the list of key strings for this toolbar. When a parent action is
        # expanded, skip it and carry its left bracket to the first sub-item so
        # the sub-items shift into the parent's slot.
        keys = []
        carry_lbc = ""
        for n in tbactions.toolbar_actions[t]:
          if n in tbactions.expanded_actions and tbactions.expanded_actions[n]:
            carry_lbc = exp_brkt_clr
            continue
          left_brkt_clr = carry_lbc or (exp_brkt_clr if n in tbactions.expanded_actions else "")
          carry_lbc = ""
          right_brkt_clr = exp_brkt_clr if not tbactions.expanded_actions.get(n, True) or \
		tbactions.actions[n].islastsubaction else ""
          keys.append("{}{sv}{}{sv}{}{sv}{}{sv}{}{sv}{}{sv}{}{sv}{}".
		format(t, n, 1 if tbactions.actions[n].enabled else 0,
			tbactions.actions[n].iconid,
			tbactions.actions[n].title, t,
			left_brkt_clr, right_brkt_clr, sv = self.SV))

        if not keys:
          continue

        indiv_toolbar_page_maker_ctr = 0

        # Add all the keys to the pages
        for key in keys:

          # If we don't have empty key slots left, add empty pages
          if not self.pages or "[key]" not in self.pages[-1]:

            # If we have navigation keys, replace the previous page's [pagenext]
            # placeholder if any
            if self.with_nav_keys and self.pages:
              self.pages[-1] = self.pages[-1].replace("[pagenext]",
							"{}{sv}PAGENEXT{sv}{sv}"
							"{sv}{sv}{}{sv}{sv}{}".
							format(page_marker(),
								t, nav_brkt_clr,
								sv = self.SV))

            # Add new pages. Mark all the new pages' keys with a unique page
            # marker.
            for i, p in enumerate(empty_new_pages):

              indiv_toolbar_page_maker_ctr += 1

              new_page = p.replace("[toolbar]", page_marker())

              # Do we have navigation keys?
              if self.with_nav_keys:

                # If we have more than one new page, replace the [pagenext]
                # placeholder in all but the last new page
                if i < last_empty_new_page_i:
                  new_page = new_page.replace("[pagenext]",
						"{}{sv}PAGENEXT{sv}{sv}{sv}{sv}"
						"{}{sv}{sv}{}".
						format(page_marker(), t, nav_brkt_clr,
							sv = self.SV))

                # Replace the first [pageprev] placeholder
                if i == 0:
                  new_page = new_page.replace("[pageprev]",
						"{}{sv}PAGEPREV{sv}{sv}{sv}{sv}"
						"{}{sv}{}{sv}".
						format(page_marker(),
							prev_page_toolbar,
							nav_brkt_clr, sv = self.SV) \
						if prev_page_toolbar else \
						"{}{sv}{sv}{sv}{sv}"
						"{sv}{sv}{}{sv}".
						format(page_marker(), nav_brkt_clr,
							sv = self.SV), 1)

                # Replace the remaining [pageprev] placeholders if any
                else:
                  new_page = new_page.replace("[pageprev]",
						"{}{sv}PAGEPREV{sv}{sv}{sv}{sv}"
						"{}{sv}{}{sv}".
						format(page_marker(), t, nav_brkt_clr,
							sv = self.SV))

              # Add the new page to the pages
              self.pages.append(new_page)

            prev_page_toolbar = t

          # Insert the next key into the pages
          self.pages[-1] = self.pages[-1].replace("[key]", key, 1)

        # Add blank keys to complete the last page for this toolbar
        self.pages[-1] = self.pages[-1].replace("[key]", "{}{sv}{sv}{sv}{sv}"
						"{sv}{sv}{sv}".
						format(page_marker(),
							sv = self.SV))

    # If we have navigation keys, replace the last [pagenext] placeholder if any
    if self.with_nav_keys and self.pages:
      self.pages[-1] = self.pages[-1].replace("[pagenext]", "{}{sv}{sv}{sv}{sv}"
						"{sv}{sv}{sv}{}".
						format(page_marker(), nav_brkt_clr,
							sv = self.SV))



  def locate_current_page(self, new_toolbar = None, last_action_pressed = None):
    """Find the new location of the current page by finding the page in the
    current set of pages that best matches it, then update the current page and
    page number
    If new_toolbar is defined, try to set the new page to the beginning of that
    toolbar
    It last_action_pressed is defined, use it to locate the current page if a
    we can't find a better matching page
    """

    self.previous_current_page = self.current_page

    # Do we have pages?
    if not self.pages:
      self.current_page = None
      self.current_page_no = None
      return

    # If we have no current page, pick the first one
    if self.current_page is None:
      self.current_page = self.pages[0]
      self.current_page_no = 0
      return

    # If we have a new toolbar, switch to the first page containing keys
    # marked with the name of the new toolbar
    if new_toolbar:
      r = re.compile("(^|{sk}){}{sv}".format(new_toolbar,
						sv = self.SV, sk = self.SK))
      for page_no, page in enumerate(self.pages):
        if r.search(page):
          self.current_page_no = page_no
          self.current_page = page
          return

    # Has any of the pages changed?
    if (len(self.previous_pages) != len(self.pages) or \
	any([self.previous_pages[i] != p for i, p in enumerate(self.pages)])):

      # Try to find a page in the new pages that matches it with regard to
      # action names and placements, regardless of their enabled status,
      # regardless of their icons and regardless of page navigation keys
      r = re.compile("^" + self.SK.join([("{}{sv}({})?({sv}[^{sk}{sv}]*){{6}}".
						format(k.toolbar, k.name, sv = self.SV,
							sk = self.SK) \
					if k.name in ("PAGEPREV", "PAGENEXT") else \
						"{}{sv}{}{sv}.?{sv}[^{sk}{sv}]"
						"*?{sv}{}{sv}{}{sv}{}{sv}{}".
						format(k.toolbar, k.name,
							k.toptext, k.bottomtext,
							k.left_brkt_clr, k.right_brkt_clr,
							sv = self.SV,
							sk = self.SK))\
					for k in [self.parse_key(ks) \
					for ks in self.current_page.\
							split(self.SK)]]) + "$")
      for page_no, page in enumerate(self.pages):
        if r.match(page):
          self.current_page_no = page_no
          self.current_page = page
          return

      # If we have a last action pressed, try to switch to the page containing
      # that action - i.e. same toolbar name and same action name...
      if last_action_pressed:
        r = re.compile("(^|{sk}){}{sv}{}{sv}".
			format(last_action_pressed.toolbar,
				last_action_pressed.name,
				sv = self.SV, sk = self.SK))
        for page_no, page in enumerate(self.pages):
          if r.search(page):
            self.current_page_no = page_no
            self.current_page = page
            return

        # ...and if the name of the last action pressed wasn't found and
        # it's a subaction of another action, try to switch to the page
        # containing the key corresponding to the parent action
        if last_action_pressed.issubactionof is not None:
          r = re.compile("(^|{sk}){}{sv}{}{sv}".
				format(last_action_pressed.toolbar,
					last_action_pressed.issubactionof,
					sv = self.SV, sk = self.SK))
          for page_no, page in enumerate(self.pages):
            if r.search(page):
              self.current_page_no = page_no
              self.current_page = page
              return

      # Try to switch to the first page containing keys marked with the name
      # of the current toolbar
      r = re.compile("(^|{sk}){}{sv}".
			format(self.current_page.split(self.SV, 1)[0].\
							split("#", 1)[0],
				sv = self.SV, sk = self.SK))
      for page_no, page in enumerate(self.pages):
        if r.search(page):
          self.current_page_no = page_no
          self.current_page = page
          return

      # Default to the first page as a last resort
      self.current_page = self.pages[0]
      self.current_page_no = 0



  def flip(self, nbpages):
    """Jump nbpages pages: before the current page if nbpages <0, after if
    nbpages >0
    Return True if the page was changed
    """

    new_page_no = min(len(self.pages) - 1,
			max(0, self.current_page_no + nbpages))

    if new_page_no == self.current_page_no:
      return False

    self.current_page_no = new_page_no
    self.previous_current_page = self.current_page
    self.current_page = self.pages[self.current_page_no]

    return True

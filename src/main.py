#!/usr/bin/env python3

import gi
import sys
import requests
from bs4 import BeautifulSoup
from os.path import expanduser, join

gi.require_version("Gtk", "3.0")
gi.require_version('Handy', '1')

from gi.repository import GObject, GLib, Gtk, Handy, Gio

class Application(Gtk.Application):

    def __init__(self):
        super().__init__(application_id='mlv.knrf.pastebin_reader')
        GLib.set_application_name('Pastebin Reader')
        GLib.set_prgname('mlv.knrf.pastebin_reader')
        self.backend  = App_Backend()

    def do_activate(self):
        window = Gtk.ApplicationWindow(application=self)
        window.set_icon_name('mlv.knrf.pastebin_reader')
        title_bar = Handy.TitleBar()
        
        header = Gtk.HeaderBar(
            title='Pastebin Reader',
            show_close_button=True)

        self.popover = Gtk.Popover()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        reload_btn = Gtk.ModelButton(label="Reload")
        reload_btn.connect("clicked", self.on_reload)

        save_btn = Gtk.ModelButton(label="Save")
        save_btn.connect("clicked", self.on_save)

        about_btn = Gtk.ModelButton(label="About")
        about_btn.connect("clicked", self.on_about)


        vbox.pack_start(reload_btn, False, True, 5)
        vbox.pack_start(save_btn, False, True, 5)
        vbox.pack_start(about_btn, False, True, 5)
        vbox.show_all()
        self.popover.add(vbox)
        self.popover.set_position(Gtk.PositionType.BOTTOM)

        btn = Gtk.MenuButton(popover=self.popover)
        icon = Gio.ThemedIcon(name="preferences-system-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        btn.add(image)
        header.add(btn)
       
        title_bar.add(header)
        window.set_titlebar(title_bar)
        #End of title bar
       
        # Items page
        scrolledwindow2 = Gtk.ScrolledWindow()
        scrolledwindow2.set_vexpand(True)
        scrolledwindow2.set_hexpand(True)

        store = self.backend.get_items()

        self.tree = Gtk.TreeView(model=store)
        self.tree.connect('cursor_changed', self.on_treeview_selection_changed)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Title", renderer, text=0)
        self.tree.append_column(column)

        column1 = Gtk.TreeViewColumn("URL")
        self.tree.append_column(column1)

        title = Gtk.CellRendererText()
        url = Gtk.CellRendererText()

        column.pack_start(title, True)
        column1.pack_start(url, True)
        column1.add_attribute(url, "text", 1)

        scrolledwindow2.add(self.tree) 

        #Reader page
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)

        text_view = Gtk.TextView()
        text_view.set_editable(False)
        text_view.set_cursor_visible(False)

        self.textbuffer = text_view.get_buffer()
        self.textbuffer.set_text(
        '''
        Text needed
        Here
        ''')

        scrolledwindow.add(text_view)
        
        #layout 
        vbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 5) 

        #Start of switch view
        self.switch_view = Gtk.StackSwitcher()
        self.switch_stack = Gtk.Stack()
        self.switch_view.set_halign(Gtk.Align.CENTER)

        self.switch_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT) 
        self.switch_stack.set_transition_duration(1000) 

        self.switch_stack.add_titled(scrolledwindow2, "tree", "Items")
        self.switch_stack.add_titled(scrolledwindow, "scrolledwindow", "Reader")

        self.switch_stack.show()
        self.switch_view.show()
        
        self.switch_view.set_stack(self.switch_stack)
        vbox.pack_start(self.switch_view,False,True,10)
        vbox.pack_start(self.switch_stack,False,True,10)
        window.add(vbox)
      
        # window setting
        window.set_default_size(720, 1300)
        window.show_all()

    
    # when the user selects a row
    def on_treeview_selection_changed(self, tview):
        # call func to get data
        url = ""
        tree_sel = tview.get_selection()
        (model,pathlist) = tree_sel.get_selected_rows()
        for path in pathlist:
            text_iter = model.get_iter(path)
            url = model.get_value(text_iter,1)

        text = self.backend.get_raw_data(url)
        if text != None:
            self.textbuffer.set_text(text)
            # switch page on switchstack
            self.switch_stack.set_visible_child(self.switch_stack.get_child_by_name("scrolledwindow"))

    def on_about(self, model_button):
        #icon = GdkPixbuf.Pixbuf.new_from_file()
        
        about = Gtk.AboutDialog()
        about.set_version("1.0.0")
        #about.set_logo(icon)
        #about.set_website()
        #about.set_license()
        about.set_comments("A pastebin.com viewer - by knrf")

        about.show_all()

    def on_save(self, model_button):
        data = self.textbuffer.get_text(self.textbuffer.get_start_iter(), self.textbuffer.get_end_iter(), False)
       
        home = expanduser("~")   
        path = join(home,"Documents")
        filename = data[0:8] + ".txt"
        filename = filename.replace(" ","")
        filename = filename.replace("\n", "")
        fullpath = join(path, filename)
        
        with open(fullpath, mode="w") as f:
            f.write(data)

    def on_reload(self, model_button):
        store = self.backend.get_items()
        if store == None:
            pass # Error
        else:
            self.tree.set_model(store)



class App_Backend:
    def __init__(self):
        self.header =  {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:77.0) Gecko/20190101 Firefox/77.0'}
        self.item_page = "https://pastebin.com/archive"
        self.root_url = "https://pastebin.com/"

    def get_items(self):
        try:
            store = Gtk.ListStore(str, str)
            r = requests.get(self.item_page, headers=self.header)
        
            if r.status_code == 200:
                bs = BeautifulSoup(r.text, "html.parser")
                table = bs.table 
                raw_items = table.find_all("td")
                for item in raw_items:
                    link = item.find("a")
                    try:
                        title = link.text
                        url = link.get('href')
                        if "/archive/" in url:
                            continue
                        store.append([title, url])
                    except AttributeError:
                        pass # pass link item
                return store
            else:
                return None
        except Exception:
            pass


    def get_raw_data(self, url):
        # add try
        full_url = self.root_url + 'raw' + url
        r = requests.get(full_url, headers=self.header)
        try:
            if r.status_code == 200:
                t = r.text
                return t
            return None
        except Exception as e:
            return None


def main():
    Handy.init()
    app = Application()
    rvalue = app.run(sys.argv)


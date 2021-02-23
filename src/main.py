#!/usr/bin/env python3

import gi
import sys
import requests
from bs4 import BeautifulSoup
from os.path import expanduser, join

gi.require_version("Gtk", "3.0")
gi.require_version('Handy', '1')

from gi.repository import GObject, GLib, Gtk, Handy, Gio
from gi.repository import GtkSource


class Application(Gtk.Application):

    def __init__(self):
        super().__init__(application_id='mlv.knrf.pastebinReader')
        GLib.set_application_name('Pastebin Reader')
        GLib.set_prgname('mlv.knrf.pastebinReader')
        self.backend  = App_Backend()
        self.lang_mang = GtkSource.LanguageManager()

    def do_activate(self):
        window = Gtk.ApplicationWindow(application=self)
        window.set_icon_name('mlv.knrf.pastebin_reader')
        window.set_titlebar(self.mk_title_bar())
        
        window.add(self.mk_switch(self.mk_item_page(), self.mk_reader_page()))
        window.set_default_size(720, 1300)
        window.show_all()
    
    def mk_title_bar(self):
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
        return title_bar
        
    def mk_item_page(self):
        scrolledwindow2 = Gtk.ScrolledWindow()
        scrolledwindow2.set_vexpand(True)
        scrolledwindow2.set_hexpand(True)

        store = self.backend.get_items()
        if store == None:
            print("No Store")

        self.tree = Gtk.TreeView(model=store)
        self.tree.connect('cursor_changed', self.on_treeview_selection_changed)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Title", renderer, text=0)
        self.tree.append_column(column)

        column1 = Gtk.TreeViewColumn("URL")
        self.tree.append_column(column1)
        
        column2 = Gtk.TreeViewColumn("Syntax")
        self.tree.append_column(column2)

        title = Gtk.CellRendererText()
        url = Gtk.CellRendererText()
        syntax = Gtk.CellRendererText()

        column.pack_start(title, True)
        column1.pack_start(url, True)
        column2.pack_start(syntax,True)
        column1.add_attribute(url, "text", 1)
        column2.add_attribute(syntax, "text", 2)

        scrolledwindow2.add(self.tree) 
        return scrolledwindow2
        
    def mk_reader_page(self):
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)

        source = GtkSource.View()
        source.set_show_line_numbers(True)
        self.textbuffer = source.get_buffer()

        scrolledwindow.add(source)
        return scrolledwindow
        
    def mk_switch(self,item_page,reader_page):
        vbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 5) 

        #Start of switch view
        self.switch_view = Gtk.StackSwitcher()
        self.switch_stack = Gtk.Stack()
        self.switch_view.set_halign(Gtk.Align.CENTER)

        self.switch_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT) 
        self.switch_stack.set_transition_duration(1000) 

        self.switch_stack.add_titled(item_page, "tree", "Items")
        self.switch_stack.add_titled(reader_page, "scrolledwindow", "Reader")

        self.switch_stack.show()
        self.switch_view.show()
        
        self.switch_view.set_stack(self.switch_stack)
        vbox.pack_start(self.switch_view,False,True,10)
        vbox.pack_start(self.switch_stack,False,True,10)
        return vbox
      
    def fix_lang(self, lang_name):
        if lang_name == "C#":
            return "c-sharp"
        if lang_name == "PHP":
            return "php"
        if lang_name == "HTML 5":
            return "html"
        if lang_name == "Bash":
            return "sh"
        if lang_name == "JavaScript":
            return "js"
        if lang_name == "C++":
            return "c++"

        return lang_name

    
    # when the user selects a row
    def on_treeview_selection_changed(self, tview):
        url = ""
        tree_sel = tview.get_selection()
        (model,pathlist) = tree_sel.get_selected_rows()
        for path in pathlist:
            text_iter = model.get_iter(path)
            url = model.get_value(text_iter,1)
            syntax = model.get_value(text_iter,2)

        text = self.backend.get_raw_data(url)
        if text != None:
            self.textbuffer.set_text(text)
            syntax = self.fix_lang(syntax)
            print(syntax) 
            lang = GtkSource.LanguageManager.get_language(self.lang_mang,str(syntax).lower())
            self.textbuffer.set_highlight_syntax(True)
            if lang != None:
                self.textbuffer.set_language(lang)
            # switch page on switchstack
            self.switch_stack.set_visible_child(self.switch_stack.get_child_by_name("scrolledwindow"))

    def on_about(self, model_button):
        #icon = GdkPixbuf.Pixbuf.new_from_file()
        about = Gtk.AboutDialog()
        about.set_version("1.1.0")
        #about.set_logo(icon)
        about.set_website("https://github.com/Frankmau5/pastebinReader")
        about.set_license("GPLv3 Read more here : https://github.com/Frankmau5/pastebinReader/blob/main/LICENSE")
        about.set_comments("A pastebin.com viewer - by knrf")

        about.show_all()

    def on_save(self, model_button):
        try:
            data = self.textbuffer.get_text(self.textbuffer.get_start_iter(), self.textbuffer.get_end_iter(), False)
       
            home = expanduser("~")   
            path = join(home,"Documents")
            filename = data[0:8] + ".txt"
            filename = filename.replace(" ","")
            filename = filename.replace("\n", "")
            fullpath = join(path, filename)
        
            with open(fullpath, mode="w") as f:
                f.write(data)
        except Exception:
            pass

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
            r = requests.get(self.item_page, headers=self.header)
            store = Gtk.ListStore(str, str, str)

            if r.status_code == 200:
                bs = BeautifulSoup(r.text, "html.parser")
                table = bs.table
                raw_items = table.find_all("tr")
                for item in raw_items:
                    link = item.find_all("a")
                    if len(link) == 2:
                       title = link[0].text
                       url = link[0].get('href')
                       syntax = link[1].text
                       store.append([title, url, syntax])
                return store
            else:
                return None

        except Exception as e:
            print(str(e))


    def get_raw_data(self, url):
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


#main() # debug only

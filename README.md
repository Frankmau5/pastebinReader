# pastebin reader
A Gtk pastebin.com reader for pinephone

#### Description

A Gtk reader for pastebin.com. I bulid this app so I can  view what is being posted to pastebin.com on my pinephone. 


#### Road map
Things I want to do 


1.Add a setting page (where you can change where files save to and name of saved files)

2.Add a button in the top menu where you can load other things a user has uploaded


#### License
GPLv3 - [read here](https://github.com/Frankmau5/pastebinReader/blob/main/LICENSE)

#### Install
Install for pinephone

`flatpak install pastebinReader-aarm64.flatpak`

Install for Desktop

`flatpak --user install pastebinReader-x86-64.flatpak`

#### Build
Remove the arch flag for x86-64 

`flatpak-builder --arch=aarch64 --repo=myrepo _flatpac  mlv.knrf.pastebinReader.json`

`flatpak build-bundle --arch=aarch64 myrepo pastebinReader.flatpak mlv.knrf.pastebinReader`

In the mlv.knrf.pastebinReader.json you will need to change finish-args and build-options.

For pinephone you need the "--socket=wayland" and for desktop you will need "--socket=fallback-x11"
unless you use wayland on your desktop 

#### Usage
There should be a desktop entry in your luncher. You might want to try to logout. 

if there is not you can run in the terminal.

`flatpak run mlv.krnf.pastebinReader` 




# pastebin reader
A Gtk pastebin.com reader for pinephone

#### Description

A Gtk reader for pastebin.com. I bulid this app so I can  view what is being posted to pastebin on my pinephone. 


#### Road map
Things I want to do 

1.Get syntax highlighting on the reader page

2.Add a setting page (where you can change where files save to and name of saved files)

3.Add a button in the top menu where you can load other things a user has uploaded


#### License
GPLv3 - [read here]()

#### Install
Install for pinephone

`flatpak install pastebinReader-aarm64.flatpak`

Install for Desktop

`flatpak install pastebinReader-x86-64.flatpak`

#### Build
Remove the arch flag for x86-64 

`flatpak-builder --arch=aarch64 --repo=myrepo _flatpac  mlv.knrf.pastebinReader.json`

`flatpak build-bundle --arch=aarch64 myrepo pastebinReader.flatpak mlv.knrf.pastebinReader`


#### Usage
There should be a desktop entry in your luncher. You might want to try to logout. 

if there is not you can run in the terminal.

`flatpak run mlv.krnf.pastebinReader` 




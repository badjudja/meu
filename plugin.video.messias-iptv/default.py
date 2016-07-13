# -*- coding: utf-8 -*-

"""
Copyright (C) 2015

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>
"""

import urllib, urllib2, sys, re, os, unicodedata
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import json, shutil, time, zipfile, stat

AddonID = 'plugin.video.messias-iptv'
Addon = xbmcaddon.Addon(AddonID)
localizedString = Addon.getLocalizedString
AddonName = Addon.getAddonInfo("name")
icon = Addon.getAddonInfo('icon')
plugin_handle = int(sys.argv[1])
addonDir = Addon.getAddonInfo('path').decode("utf-8")
fanart = xbmc.translatePath(os.path.join(addonDir, 'fanart.jpg'))
icon = xbmc.translatePath(os.path.join(addonDir, 'icon.png'))

LOCAL_VERSION_FILE = os.path.join(os.path.join(addonDir), 'version.xml' )
REMOTE_VERSION_FILE = "http://dofundo.mooo.com/version.xml"

online_m3u = 'http://dofundo.mooo.com/Ptlista.m3u'
local_m3u = 'http://dofundo.mooo.com/Ptlista2.m3u'
pt_m3u = 'http://dofundo.mooo.com/Ptlista2.m3u'
online_xml = 'http://dofundo.mooo.com/lista.m3u'
local_xml = 'http://dofundo.mooo.com/lista2.m3u'
algas_m3u = 'http://pastebin.com/raw/6UwwrXRN'
brasil_m3u = 'http://pastebin.com/raw/HyFjh35W'
mega_xml = 'http://pastebin.com/raw/vHQ5EBLq'

xml_regex = '<title>(.*?)</title>\s*<link>(.*?)</link>\s*<thumbnail>(.*?)</thumbnail>'
m3u_thumb_regex = 'tvg-logo=[\'"](.*?)[\'"]'
m3u_regex = '#(.+?),(.+)\s*(.+)\s*'

u_tube = 'http://www.youtube.com'

def checkforupdates(url,loc):
        xbmc.log('Start check for updates')
    	try:
		data = urllib2.urlopen(url).read()
		xbmc.log('read xml remote data:' + data)
	except:
		data = ""
		xbmc.log('fail read xml remote data:' + url )
    	try:
		f = open(loc,'r')
		data2 = f.read().replace("\n\n", "")
		f.close()
		xbmc.log('read xml local data:' + data2)
	except:
		data2 = ""
		xbmc.log('fail read xml local data')

        version_publicada = find_single_match(data,"<version>([^<]+)</version>").strip()
        tag_publicada = find_single_match(data,"<tag>([^<]+)</tag>").strip()

        version_local = find_single_match(data2,"<version>([^<]+)</version>").strip()
        tag_local = find_single_match(data,"<tag>([^<]+)</tag>").strip()

        try:
            numero_version_publicada = int(version_publicada)
            xbmc.log('number remote version:' + version_publicada)
            numero_version_local = int(version_local)
            xbmc.log('number local version:' + version_local)
        except:
            version_publicada = ""
            
            xbmc.log('number local version:' + version_local )
            xbmc.log('Check fail !@*')
        if version_publicada!="" and version_local!="":
            if (numero_version_publicada > numero_version_local):
                AddonID = 'plugin.video.messias-iptv'
                addon       = xbmcaddon.Addon(AddonID)
                addonname   = addon.getAddonInfo('name')
                extpath = os.path.join(xbmc.translatePath("special://home/addons/").decode("utf-8")) 
                addon_data_dir = os.path.join(xbmc.translatePath("special://userdata/addon_data" ).decode("utf-8"), AddonID) 
                dest = addon_data_dir + '/lastupdate.zip'                
                
                UPDATE_URL = 'http://raw.github.com/badjudja/meu/master/plugin.video.messias-iptv-' + tag_publicada + '.zip'
                xbmc.log('START DOWNLOAD UPDATE:' + UPDATE_URL)
                
                DownloaderClass(UPDATE_URL,dest)  

                import ziptools
                unzipper = ziptools.ziptools()
                unzipper.extract(dest,extpath)
                
                line7 = 'New version installed .....'
                line8 = 'Version: ' + tag_publicada 
                
                xbmcgui.Dialog().ok('Messias IpTv', line7, line8)
                
                if os.remove( dest ): xbmc.log('TEMPORARY ZIP REMOVED') 
            else:
                AddonID = 'plugin.video.messias-iptv'
                addon = xbmcaddon.Addon(AddonID)
                addonname = addon.getAddonInfo('name')
                icon = xbmcaddon.Addon(AddonID).getAddonInfo('icon')
                xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(addonname,"Check updates: no update is available", 3200, icon))
                xbmc.log('No updates are available' )
				
def find_single_match(data,patron,index=0):
    try:
        matches = re.findall( patron , data , flags=re.DOTALL )
        return matches[index]
    except:
        return ""
    
percent = 0
def DownloaderClass(url,dest):
    dp = xbmcgui.DialogProgress()
    dp.create("Messias IpTv ZIP DOWNLOADER","Downloading File",url)
    urllib.urlretrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))
        

def removeAccents(s):
	return ''.join((c for c in unicodedata.normalize('NFD', s.decode('utf-8')) if unicodedata.category(c) != 'Mn'))
					
def read_file(file):
    try:
        f = open(file, 'r')
        content = f.read()
        f.close()
        return content
    except:
        pass

def addon_log(string):
    if debug == 'true':
        xbmc.log("[addon.messias-iptv-%s]: %s" %(addon_version, string))

def make_request(url, headers=None):
        try:
            if headers is None:
                headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:19.0) Gecko/20100101 Firefox/19.0'}
            req = urllib2.Request(url,None,headers)
            response = urllib2.urlopen(req)
            data = response.read()
            response.close()
            return data
        except urllib2.URLError, e:
            addon_log('URL: '+url)
            if hasattr(e, 'code'):
                addon_log('We failed with error code - %s.' % e.code)
                xbmc.executebuiltin("XBMC.Notification(messias-iptv,We failed with error code - "+str(e.code)+",10000,"+icon+")")
            elif hasattr(e, 'reason'):
                addon_log('We failed to reach a server.')
                addon_log('Reason: %s' %e.reason)
                xbmc.executebuiltin("XBMC.Notification(messias-iptv,We failed to reach a server. - "+str(e.reason)+",10000,"+icon+")")			
			
			
def main():
	add_dir('[B]<<<  Pesquisar  >>>[/B]', 'searchlink', 99, icon, fanart)
	if len(online_m3u) > 0:	
		add_dir('[COLOR magenta][B]>> Nacional 1 <<[/B][/COLOR]', u_tube, 2, icon, fanart)
	if len(local_m3u) > 0:	
		add_dir('[COLOR magenta][B]>> Nacional 2 <<[/B][/COLOR]', u_tube, 3, icon, fanart)
	if len(pt_m3u) > 0:	
		add_dir('[COLOR magenta][B]>> Nacional 3 <<[/B][/COLOR]', u_tube, 9, icon, fanart)
	if len(online_xml) > 0:	
		add_dir('[COLOR cyan][B]>> Internacional 1<<[/B][/COLOR]', u_tube, 4, icon, fanart)
	if len(local_xml) > 0:	
		add_dir('[COLOR lime][B]>> Internacional 2 <<[/B][/COLOR]', u_tube, 5, icon, fanart)		
	if len(algas_m3u) > 0:	
		add_dir('[COLOR blue][B]>> TV Algas <<[/B][/COLOR]', u_tube, 6, icon, fanart)	
	if len(brasil_m3u) > 0:	
		add_dir('[COLOR green][B]>> Lista Brasil <<[/B][/COLOR]', u_tube, 7, icon, fanart)	
	if len(mega_xml) > 0:	
		add_dir('[COLOR red][B]>> TV Mega <<[/B][/COLOR]', u_tube, 8, icon, fanart)	
	if (len(online_m3u) < 1 and len(local_m3u) < 1 and len(online_xml) < 1 and len(local_xml) < 1 and len(algas_m3u) < 1 and len(brasil_m3u) < 1 and len(mega_xml) < 1 and len(pt_m3u) < 1 ):		
		mysettings.openSettings()
		xbmc.executebuiltin("Container.Refresh")		

def search(): 	
	try:
		keyb = xbmc.Keyboard('', 'Enter search text')
		keyb.doModal()
		if (keyb.isConfirmed()):
			searchText = urllib.quote_plus(keyb.getText()).replace('+', ' ')
		if len(online_m3u) > 0:		
			content = make_request(online_m3u)
			match = re.compile(m3u_regex).findall(content)
			for thumb, name, url in match:
				if re.search(searchText, removeAccents(name.replace('Đ', 'D')), re.IGNORECASE):
					m3u_playlist(name, url, thumb)	
		if len(local_m3u) > 0:		
			content = make_request(local_m3u)
			match = re.compile(m3u_regex).findall(content)		
			for thumb, name, url in match:
				if re.search(searchText, removeAccents(name.replace('Đ', 'D')), re.IGNORECASE):
					m3u_playlist(name, url, thumb)	
		if len(online_xml) > 0:					
			content = make_request(online_xml)
			match = re.compile(m3u_regex).findall(content)	
			for thumb, name, url in match:
				if re.search(searchText, removeAccents(name.replace('Đ', 'D')), re.IGNORECASE):
					m3u_playlist(name, url, thumb)	
		if len(local_xml) > 0:		
			content = make_request(local_xml)
			match = re.compile(m3u_regex).findall(content)		
			for thumb, name, url in match:
				if re.search(searchText, removeAccents(name.replace('Đ', 'D')), re.IGNORECASE):
					m3u_playlist(name, url, thumb)	
		if len(algas_m3u) > 0:		
			content = make_request(algas_m3u)
			match = re.compile(m3u_regex).findall(content)
			for thumb, name, url in match:
				if re.search(searchText, removeAccents(name.replace('Đ', 'D')), re.IGNORECASE):
					m3u_playlist(name, url, thumb)	
		if len(brasil_m3u) > 0:		
			content = make_request(brasil_m3u)
			match = re.compile(m3u_regex).findall(content)
			for thumb, name, url in match:
				if re.search(searchText, removeAccents(name.replace('Đ', 'D')), re.IGNORECASE):
					m3u_playlist(name, url, thumb)		
		if len(mega_xml) > 0:					
			content = make_request(mega_xml)
			match = re.compile(xml_regex).findall(content)	
			for name, url, thumb in match:
				if re.search(searchText, removeAccents(name.replace('Đ', 'D')), re.IGNORECASE):
					xml_playlist(name, url, thumb)	
		if len(pt_m3u) > 0:		
			content = make_request(pt_m3u)
			match = re.compile(m3u_regex).findall(content)
			for thumb, name, url in match:
				if re.search(searchText, removeAccents(name.replace('Đ', 'D')), re.IGNORECASE):
					m3u_playlist(name, url, thumb)						
	except:
		pass
		
def m3u_online():		
	content = make_request(online_m3u)
	match = re.compile(m3u_regex).findall(content)
	for thumb, name, url in match:
		try:
			m3u_playlist(name, url, thumb)
		except:
			pass
			
def xml_online():			
	content = make_request(online_xml)
	match = re.compile(m3u_regex).findall(content)
	for thumb, name, url in match:	
		try:
			m3u_playlist(name, url, thumb)
		except:
			pass
			
def m3u_local():
	content = make_request(local_m3u)
	match = re.compile(m3u_regex).findall(content)
	for thumb, name, url in match:	
		try:
			m3u_playlist(name, url, thumb)
		except:
			pass

def xml_local():		
	content = make_request(local_xml)
	match = re.compile(m3u_regex).findall(content)
	for thumb, name, url in match:	
		try:
			m3u_playlist(name, url, thumb)
		except:
			pass
def m3u_algas():		
	content = make_request(algas_m3u)
	match = re.compile(m3u_regex).findall(content)
	for thumb, name, url in match:	
		try:
			m3u_playlist(name, url, thumb)
		except:
			pass
def m3u_brasil():		
	content = make_request(brasil_m3u)
	match = re.compile(m3u_regex).findall(content)
	for thumb, name, url in match:	
		try:
			m3u_playlist(name, url, thumb)
		except:
			pass		
def xml_mega():			
	content = make_request(mega_xml)
	match = re.compile(m3u_regex).findall(content)
	for thumb, name, url in match:
		try:
			m3u_playlist(name, url, thumb)
		except:
			pass	
def m3u_pt():		
	content = make_request(pt_m3u)
	match = re.compile(m3u_regex).findall(content)
	for thumb, name, url in match:	
		try:
			m3u_playlist(name, url, thumb)
		except:
			pass			
def m3u_playlist(name, url, thumb):	
	name = re.sub('\s+', ' ', name).strip()			
	url = url.replace('"', ' ').replace('&amp;', '&').strip()
	if ('youtube.com/user/' in url) or ('youtube.com/channel/' in url) or ('youtube/user/' in url) or ('youtube/channel/' in url):
		if 'tvg-logo' in thumb:
			thumb = re.compile(m3u_thumb_regex).findall(str(thumb))[0].replace(' ', '%20')			
			add_dir(name, url, '', thumb, thumb)			
		else:	
			add_dir(name, url, '', icon, fanart)
	else:
		if 'youtube.com/watch?v=' in url:
			url = 'plugin://plugin.video.youtube/play/?video_id=%s' % (url.split('=')[-1])
		elif 'dailymotion.com/video/' in url:
			url = url.split('/')[-1].split('_')[0]
			url = 'plugin://plugin.video.dailymotion_com/?mode=playVideo&url=%s' % url	
		else:			
			url = url
		if 'tvg-logo' in thumb:				
			thumb = re.compile(m3u_thumb_regex).findall(str(thumb))[0].replace(' ', '%20')
			add_link(name, url, 1, thumb, thumb)			
		else:				
			add_link(name, url, 1, icon, fanart)	
					
def xml_playlist(name, url, thumb):
	name = re.sub('\s+', ' ', name).strip()			
	url = url.replace('"', ' ').replace('&amp;', '&').strip()
	if ('youtube.com/user/' in url) or ('youtube.com/channel/' in url) or ('youtube/user/' in url) or ('youtube/channel/' in url):
		if len(thumb) > 0:	
			add_dir(name, url, '', thumb, thumb)			
		else:	
			add_dir(name, url, '', icon, fanart)
	else:
		if 'youtube.com/watch?v=' in url:
			url = 'plugin://plugin.video.youtube/play/?video_id=%s' % (url.split('=')[-1])
		elif 'dailymotion.com/video/' in url:
			url = url.split('/')[-1].split('_')[0]
			url = 'plugin://plugin.video.dailymotion_com/?mode=playVideo&url=%s' % url	
		else:			
			url = url
		if len(thumb) > 0:		
			add_link(name, url, 1, thumb, thumb)			
		else:			
			add_link(name, url, 1, icon, fanart)	
	
def play_video(url):
	media_url = url
	item = xbmcgui.ListItem(name, path = media_url)
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
	return


def get_params():
	param = []
	paramstring = sys.argv[2]
	if len(paramstring)>= 2:
		params = sys.argv[2]
		cleanedparams = params.replace('?', '')
		if (params[len(params)-1] == '/'):
			params = params[0:len(params)-2]
		pairsofparams = cleanedparams.split('&')
		param = {}
		for i in range(len(pairsofparams)):
			splitparams = {}
			splitparams = pairsofparams[i].split('=')
			if (len(splitparams)) == 2:
				param[splitparams[0]] = splitparams[1]
	return param

def add_dir(name, url, mode, iconimage, fanart):
	u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name) + "&iconimage=" + urllib.quote_plus(iconimage)
	ok = True
	liz = xbmcgui.ListItem(name, iconImage = "DefaultFolder.png", thumbnailImage = iconimage)
	liz.setInfo( type = "Video", infoLabels = { "Title": name } )
	liz.setProperty('fanart_image', fanart)
	if ('youtube.com/user/' in url) or ('youtube.com/channel/' in url) or ('youtube/user/' in url) or ('youtube/channel/' in url):
		u = 'plugin://plugin.video.youtube/%s/%s/' % (url.split( '/' )[-2], url.split( '/' )[-1])
		ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = liz, isFolder = True)
		return ok		
	ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = liz, isFolder = True)
	return ok

def add_link(name, url, mode, iconimage, fanart):
	u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name) + "&iconimage=" + urllib.quote_plus(iconimage)	
	liz = xbmcgui.ListItem(name, iconImage = "DefaultVideo.png", thumbnailImage = iconimage)
	liz.setInfo( type = "Video", infoLabels = { "Title": name } )
	liz.setProperty('fanart_image', fanart)
	liz.setProperty('IsPlayable', 'true') 
	ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = liz)  
	
	
params = get_params()
url = None
name = None
mode = None
iconimage = None

try:
	url = urllib.unquote_plus(params["url"])
except:
	pass
try:
	name = urllib.unquote_plus(params["name"])
except:
	pass
try:
	mode = int(params["mode"])
except:
	pass
try:
	iconimage = urllib.unquote_plus(params["iconimage"])
except:
	pass  

print "Mode: " + str(mode)
print "URL: " + str(url)
print "Name: " + str(name)
print "iconimage: " + str(iconimage)		

if mode == None or url == None or len(url) < 1:
	main()

elif mode == 1:
	play_video(url)


elif mode == 2:
	m3u_online()
	
elif mode == 3:
	m3u_local()
	
elif mode == 4:
	xml_online()
	
elif mode == 5:
	xml_local()	
	
elif mode == 6:
	m3u_algas()	
	
elif mode == 7:
	m3u_brasil()
	
elif mode == 8:
	xml_mega()
	
elif mode == 9:
	m3u_pt()
	
elif mode == 99:
	search()
	
xbmcplugin.endOfDirectory(plugin_handle)
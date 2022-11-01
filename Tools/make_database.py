import discid
import musicbrainzngs
import json

class Cddb:
	def __init__(self):
		self.cddb = {}

	def init(self):
		cddb_size = 101
		for slot in range(1, cddb_size):
			self.cddb.update({str(slot):None})

	def add_disc(self,disc_info):
		try:
			ip_slot = input ("What slot will this CD be placed in? ")
			self.cddb.update({ip_slot:disc_info})
		except:
			print('Invalid input!!')
		

	def rem_disc(self,slot_num):
		slot_num = str(slot_num)
		self.cddb.update({slot_num:None})

	def read(self):
		try:
			with open("cd_database.json", "r") as infile:
				self.cddb = json.load(infile)
            
		except:
			print("There was a problem reading database!!")
		# read def
		

	def write(self):
		try:
			with open("cd_database.json", "w") as outfile:
				json.dump(self.cddb,outfile,indent=2)
            
		except:
			print("There was a problem writing database!!")

	def info(self,slot_num):
		slot_num = str(slot_num)
		if self.cddb[slot_num] == None:
			return 'None'
		else:
			return self.cddb[slot_num]['disc']['release-list'][0]['title']
		    
	def info_all(self,slot_num):
            slot_num = str(slot_num)
            if self.cddb[slot_num] == None:
                return 'None'
            else:
                tracks = self.cddb[slot_num]['disc']['release-list'][0]['medium-list'][0]['track-count']
                song_list = []
                for track in range(tracks):
                    song = self.cddb[slot_num]['disc']['release-list'][0]['medium-list'][0]['track-list'][track]['recording']['title']
                    length = self.cddb[slot_num]['disc']['release-list'][0]['medium-list'][0]['track-list'][track]['recording']['length']
                    position = self.cddb[slot_num]['disc']['release-list'][0]['medium-list'][0]['track-list'][track]['position']
                    length = int(length)
                    ##print (f"{position}\t {song}\t\t\t\t\t Time (mS) {length}")
                    song_list.append(song)
                return song_list
			 #self.cddb[slot_num]['disc']['release-list'][0]['title']



musicbrainzngs.set_useragent("python-discid-example", "0.1", "your@mail")
disc = discid.read()
cddb = {}

#print(f"Disc ID {disc}")


try:
    result = musicbrainzngs.get_releases_by_discid(disc.id,
                                                   includes=["artists", "recordings"])
except musicbrainzngs.ResponseError:
    print("Disc not found or bad response")
    
else:
    if result.get("disc"):
        print("CD Artist:\t%s" %
              result["disc"]["release-list"][0]["artist-credit-phrase"])
        print("CD Album title:\t%s" % result["disc"]["release-list"][0]["title"]+"\r\n")
        
    elif result.get("cdstub"):
        #print(f"artist: {result["cdstub"]["artist"]}")
        
        print("title:\t" % result["cdstub"]["title"])
        
#print (result['disc']['release-list'][0]['medium-list'][0]['track-list'])       #['track-list'][1]['recording']['title']) # last number is track
#print (result['disc']['release-list'][0]['medium-list'][0]['track-count']) #['track-list'][1]['recording']['title'])

#try:
#	ip_slot = int(input ("What slot will this CD be placed in? "))
#except:
#	print('Invalid input!!')


#cddb.update({ip_slot:result})

#json_object = json.dumps(cddb,outfile, indent = 2)

#try:
#	with open("cd_database.json", "w") as outfile:
#            json.dump(cddb,outfile,indent=2)
            
#except:
#	print("There was a problem creating database!!")


#tracks = cddb[ip_slot]['disc']['release-list'][0]['medium-list'][0]['track-count']


#for track in range(tracks):
#    song = result['disc']['release-list'][0]['medium-list'][0]['track-list'][track]['recording']['title']
#    length = result['disc']['release-list'][0]['medium-list'][0]['track-list'][track]['recording']['length']
#    position = result['disc']['release-list'][0]['medium-list'][0]['track-list'][track]['position']
#    length = int(length)
#    print (f"{position}\t {song}\t\t\t\t\t Length {length}")



db = Cddb()

db.read()

album_list=['']
for album in db.cddb:
    ##song =  db.info_all(album)
    al_title = db.info(album)
    print (album, " ", al_title)
    if al_title !="None":
        album_list.append(al_title)
        
        
#db.add_disc(result)

#db.write()
        
#song_list.sort()
        
        
        
        
################ scrap code below here #############################

def res_info(data):
		if data == None:
			return 'None'
		else:
			return data['disc']['release-list'][0]['title']
		    
		    
		    



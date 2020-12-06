from re import  compile,match
class Disk_toc:
    catalog = ""
    type = None
    __CD_DA = 0
    __CD_ROM = 1
    __CD_ROM_XA = 2
    cdtext_languages = []
    languages_map = []
    global_cd_text = None
    tracks = []
    
    def get_from_toc_file (self,toc_file):
        catalog_regxp = compile ("CATALOG \"(.*)\"")
        cdda_regxp = compile ("CD_DA")
        cdrom_regxp = compile ("CD_ROM")
        cdromxa_regxp = compile ("CD_ROM_XA")
        track_regxp = compile("TRACK\s+(.*)")
        copy_regxp = compile ("(.*)\s*COPY")
        preemph_regxp = compile ("(.*)\s*PRE_EMPHASIS")
        two_chans_regxp = compile ("TWO_CHANNEL_AUDIO")
        four_chans_regxp = compile ("FOUR_CHANNEL_AUDIO")
        isrc_regxp = compile ("ISRC \"(.*)\"")
        silence_regexp = compile("SILENCE\s*(.*)")
        zero_regexp = compile("ZERO\s*(.*)")
        file_regexp = compile ("FILE \"(.*)\"\s*(.*)\s+(\d\d:\d\d:\d\d)*")
        audiofile_regep = compile ("AUDIOFILE \"(.*)\"\s*(.*)\s+(\d\d:\d\d:\d\d)*")
        datafile_regexp = compile ("DATAFILE \"(.*)\"\s*(.*)\s+(\d\d:\d\d:\d\d)*")
        fifo_regexp = compile ("FIFO \"(.*)\"\s*(.*)\s+(.*)")
        start_regexp = compile("START\s*(.*)")
        pregap_regexp = compile("PREGAP\s*(.*)")
        index_regexp = compile("INDEX\s*(.*)")
        cdtext_regxp = compile ("CD_TEXT")
        language_map_regexp = compile ("\s*LANGUAGE_MAP\s+{")
        language_num = compile ("\s*(.*) : (.*).*")
        language_regexp = compile ("\s*LANGUAGE\s+(.*)\s+{")
        
        global_section = True
        line = " "
        
        track_num = -1
        
        while True:
            line = toc_file.readline()
            
            if line == "":
                break
             
            line = line.strip()
           
            matched = catalog_regxp.match (line)
            if matched != None:
                self.catalog = matched.group(1)
            
#===============================================================================
#            CD TYPE
#===============================================================================
            matched = cdda_regxp.match (line)
            if matched != None:
                self.type = self.__CD_DA
            
            matched = cdrom_regxp.match (line)
            if matched != None:
                self.type = self.__CD_ROM
            
            matched = cdromxa_regxp.match (line)
            if matched != None:
                    self.type = self.__CD_ROM_XA
            
            matched = cdtext_regxp.match (line)
            if matched != None:
                subline = " "
#===============================================================================
#                CD_TEXT
#===============================================================================
                while subline != "}":
                    subline = toc_file.readline()
                    subline = subline.strip()
                    
                    submatched = language_map_regexp.match(subline)
                    if submatched != None:
                        subsubline = " "
#===============================================================================
#                        Language Map 
#===============================================================================
                        while subsubline != "}":
                            subsubline = toc_file.readline()
                            subsubline = subsubline.strip()
                            
                            subsubmatched = language_num.match(subsubline)
                            if subsubmatched != None:
                                index = int(subsubmatched.group(1))
                                self.languages_map[index] =  subsubmatched.group(2)
                        
                            
                        
                    
                    submatched = language_regexp.match(subline)
                    if submatched != None:
                        num_language = int(submatched.group(1))
                        section = self.__read_section(toc_file)
                        cdt_inst = self.get_cd_text_values(section)
                        cdt_inst.language = num_language
                        
                        if global_section:
                            self.global_cd_text = cdt_inst
                        else:
                            self.tracks[track_num].cd_text.append(cdt_inst)
            
#===============================================================================
#            TRACK SECTION
#===============================================================================
            matched = track_regxp.match (line)
            if matched != None:
                global_section = False
                track_num += 1
                self.tracks.append(Track())
        
                if matched.group(1) == "AUDIO":
                    self.tracks[track_num].type = self.tracks[track_num]._AUDIO
                elif matched.group(1) == "MODE1":
                    self.tracks[track_num].type = self.tracks[track_num]._MODE1
                elif matched.group(1) == "MODE1_RAW":
                    self.tracks[track_num].type = self.tracks[track_num]._MODE1_RAW
                elif matched.group(1) == "MODE2":
                    self.tracks[track_num].type = self.tracks[track_num]._MODE2
                elif matched.group(1) == "MODE2_FORM1":
                    self.tracks[track_num].type = self.tracks[track_num]._MODE2_FORM1
                elif matched.group(1) == "MODE2_FORM2":
                    self.tracks[track_num].type = self.tracks[track_num]._MODE2_FORM2
                elif matched.group(1) == "MODE2_FORM_MIX":
                    self.tracks[track_num].type = self.tracks[track_num]._MODE2_FORM_MIX
                elif matched.group(1) == "MODE2_RAW":
                    self.tracks[track_num].type = self.tracks[track_num]._MODE2_RAW
                
                    
            match = copy_regxp.match(line)
            if match != None:
                if match.group(1).strip() == "NO":
                    self.tracks[track_num].copy = False
                else:
                    self.tracks[track_num].copy = True
                    
            match = preemph_regxp.match(line)
            if match != None:
                if match.group(1).strip() == "NO":
                    self.tracks[track_num].pre_emphasis = False
                else:
                    self.tracks[track_num].pre_emphasis = True
                    
            match = two_chans_regxp.match(line)
            if match != None:
                self.tracks[track_num].two_audio_channels = True
                    
            match = four_chans_regxp.match(line)
            if match != None:
                self.tracks[track_num].four_audio_channels = True
                    
            match = isrc_regxp.match(line)
            if match != None:
                self.tracks[track_num].isrc = match.group(1)

            match = silence_regexp.match(line)
            if match != None:
                self.tracks[track_num].silence = match.group(1)
            
            match = zero_regexp.match(line)
            if match != None:
                self.tracks[track_num].zero = match.group(1)
            
            match = file_regexp.match(line)
            if match != None:
                self.tracks[track_num].filename = match.group(1)
                self.tracks[track_num].file_start= match.group(2)
                if len(match.groups()) > 2:
                    if match.group(3) != None:
                        self.tracks[track_num].file_length = match.group(3)
            
            match = audiofile_regep.match(line)
            if match != None:
                self.tracks[track_num].filename = match.group(1)
                self.tracks[track_num].file_start = match.group(2)
                if len(match.groups()) > 2:
                    if match.group(3) != None:
                        self.tracks[track_num].file_length = match.group(3)
            
            match = datafile_regexp.match(line)
            if match != None:
                self.tracks[track_num].filename = match.group(1)
                self.tracks[track_num].file_start = match.group(2)
                if len(match.groups()) > 2:
                    if match.group(3) != None:
                        self.tracks[track_num].file_length = match.group(3)
            
            match = fifo_regexp.match(line)
            if match != None:
                self.tracks[track_num].fifo_path = match.group(1)
                self.tracks[track_num].fifo_length = match.group(2)
            
            match = start_regexp.match(line)
            if match != None:
                self.tracks[track_num].start = match.group(1)
            
            match = pregap_regexp.match(line)
            if match != None:
                self.tracks[track_num].pregap = match.group(1)
            
            match = index_regexp.match(line)
            if match != None:
                self.tracks[track_num].index = match.group(1)
                    
    def get_num_tracks(self):
        return len(self.tracks)
    
    def __read_section (self,fh):
        line = ""
        section = []
        while line != "}":
            line = fh.readline()
            line = line.strip()
            
            if line != "}":
                section.append(line)
        
        return section
    
    def get_cd_text_values (self,cdtext_section):
        title_regexp = compile ("\s*TITLE \"(.*)\"")
        performer_regexp = compile ("\s*PERFORMER \"(.*)\"")
        songwriter_regexp = compile ("\s*SONGWRITER \"(.*)\"")
        composer_regexp = compile ("\s*COMPOSER \"(.*)\"")
        aranger_regexp = compile ("\s*ARANGER \"(.*)\"")
        message_regexp = compile ("\s*MESSAGE \"(.*)\"")
        diskid_regexp = compile ("\s*DISC_ID\s+(.*)")
        genre_regexp = compile("\s*GENRE\s+(.*)")
        upcean_regexp = compile ("\s*UPC_EAN \"(.*)\"")
        isrc_regexp = compile ("\s*ISRC \"(.*)\"")
        
        cdt_inst = Cd_text()
        
        for line in cdtext_section:
            subsubmatched = title_regexp.match (line)
            if subsubmatched != None:
                cdt_inst.title = subsubmatched.group(1)
            
            subsubmatched = performer_regexp.match (line)
            if subsubmatched != None:
                cdt_inst.performer = subsubmatched.group(1)
            
            subsubmatched = songwriter_regexp.match (line)
            if subsubmatched != None:
                cdt_inst.songwriter = subsubmatched.group(1)
            
            subsubmatched = composer_regexp.match (line)
            if subsubmatched != None:
                cdt_inst.composer = subsubmatched.group(1)
            
            subsubmatched = aranger_regexp.match (line)
            if subsubmatched != None:
                cdt_inst.aranger = subsubmatched.group(1)
                
            subsubmatched = message_regexp.match (line)
            if subsubmatched != None:
                cdt_inst.message = subsubmatched.group(1)
            
            subsubmatched = diskid_regexp.match (line)
            if subsubmatched != None:
                cdt_inst.disc_id = subsubmatched.group(1)
            
            subsubmatched = genre_regexp.match (line)
            if subsubmatched != None:
                cdt_inst.genre = subsubmatched.group(1)
            
            subsubmatched = upcean_regexp.match (line)
            if subsubmatched != None:
                cdt_inst.upc_ean = subsubmatched.group(1)
            
            subsubmatched = isrc_regexp.match (line)
            if subsubmatched != None:
                cdt_inst.isrc = subsubmatched.group(1)
        
        return cdt_inst
        
class Track:
    type = None
    _AUDIO = 0
    _MODE1 = 1
    _MODE1_RAW = 2
    _MODE2 = 3
    _MODE2_FORM1 = 4
    _MODE2_FORM2 = 5
    _MODE2_FORM_MIX = 6
    _MODE2_RAW = 7
    cd_text = []
    copy = False
    pre_emphasis = ""
    two_audio_channels = False
    four_audio_channels = False
    isrc = ""
    silence = ""
    zero = ""
    filename = ""
    file_start = ""
    file_length = ""
    fifo_path = ""
    fifo_length = ""
    start = ""
    pregap = ""
    index = ""
    
    def __init__(self):
        self.cd_text = []

class Cd_text:
    title = ""
    performer = ""
    songwriter = ""
    composer = ""
    aranger = ""
    message = ""
    disc_id = ""
    genre = ""
    upc_ean = ""
    isrc = ""
    language = -1
    
dt = Disk_toc()
fh = open ("/home/dsolimando/test1.toc","r")
dt.get_from_toc_file(fh)  
for track in dt.tracks:
    print track.type 
    for cdtext in track.cd_text:
        print "=========CD TEXT INFO========="
        print cdtext.title
        print cdtext.performer
        print cdtext.songwriter
        print cdtext.composer
        print "==============================="
    print track.copy
    print track.pre_emphasis
    print track.two_audio_channels
    print track.four_audio_channels
    print track.isrc
    print track.silence
    print track.zero
    print track.filename 
    print track.file_start
    print track.file_length
    print track.fifo_path
    print track.fifo_length
    print track.start 
    print track.pregap 
    print track.index 
        
        
    
    
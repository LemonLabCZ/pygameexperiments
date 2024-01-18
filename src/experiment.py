# stimulus class definition
class stimulus:
    # Instance initialization
    def __init__(self, kind, content, position,size,color,startTime, duration,iti,condition,trigger):
        self.stimType = kind
        self.stimContent = content
        self.size = size
        self.pos = position
        self.color = color
        self.dur = duration
        self.iti = iti
        self.trigger = trigger
        self.response = ''
        self.rt = -1
        self.onset = -1
        self.startTime = startTime
        self.cond = condition

    # Present stimulus and collect responses ===============================================
    def present(self, screen, screenSize, screenColor, terminateByResponse):
        # stimulus definition and presentattion -------------------------------------------    
        if self.stimType == 'sound':
            sound2play = pygame.mixer.Sound(self.stimContent)
            trialDuration = round(sound2play.get_length()*1000) + random.randint(self.isi[0],self.isi[1])
            stimDuration = round(sound2play.get_length()*1000)
            
            pygame.mixer.Sound.play(sound2play)
            if self.trigger > 0:
                sendTrigger(self.trigger)
            onset = datetime.now()
        
        else:
            trialDuration = self.dur + random.randint(self.iti[0],self.iti[1])
            stimDuration = self.dur

            if self.stimContent =='rectangle':
                pygame.draw.rect(screen, self.color,(round(self.pos[0] - self.size[0]/2),round(self.pos[1] - self.size[1]/2),round(self.size[0]), round(self.size[1])))
            if self.stimContent == 'circle':
                pygame.draw.circle(screen, self.color,(self.pos[0],self.pos[1]/2),round(self.size))
        
            if self.stimType == 'picture':
                img = pygame.image.load(self.stimContent)
                img = pygame.transform.scale(img, (self.size[0], self.size[1]))
                img.convert()
                rect = img.get_rect()
                rect.center = (self.pos[0],self.pos[1])
                screen.blit(img, rect)
                
            if self.stimType == 'text':
                font = pygame.font.SysFont(None, self.size)
                text2display = font.render(self.stimContent, True, self.color)
                rect = text2display.get_rect()
                rect.centerx = self.pos[0]
                rect.centery = self.pos[1]
                screen.blit(text2display, rect)
        
            pygame.display.update()
            if self.trigger > 0:
                sendTrigger(self.trigger)
            onset = datetime.now()

        # Response collection -------------------------------------------         
        listen = True
        stimOn = True
        response = -1
        responseTime = -1
        position = []
        
        while listen:
            t = (datetime.now() - onset).seconds * 1000 + round((datetime.now() - onset).microseconds/1000)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and response == -1:
                    response = f"K{event.key}"                  
                    responseTime = t
                    print(f"trial #{ii}; onset = {(onset - self.startTime).seconds + (onset - self.startTime).microseconds/1000000}; Keyboard code {event.key}; rt = {t} ms")                
                    if terminateByResponse:
                        return onset, response, responseTime

                if event.type == pygame.MOUSEBUTTONDOWN and response == -1:
                    response = f"M{event.button}"                 
                    responseTime = t
                    position = event.pos
                    print(f"trial #{ii}; onset = {(onset - self.startTime).seconds + (onset - self.startTime).microseconds/1000000}; Mouse button {event.button}; rt = {t} ms, position = {event.pos}")                
                    if terminateByResponse:
                        return onset, response, responseTime, position

            if t > stimDuration and stimOn:
                    screen.fill(screenColor)
                    pygame.display.update()
                    stimOn = False
               
            if t > trialDuration:
                listen = False
        
        return onset, response, responseTime, position
    
    # write results to pandas dataframe  ===============================================
    def writeLog(self,dataLog,ind):
        dataLog.at[ii,'stimOnset'] = (self.onset - self.startTime).seconds + (self.onset - self.startTime).microseconds/1000000
        dataLog.at[ii,'stimType'] = self.stimType
        dataLog.at[ii,'stimCont'] = self.stimContent
        dataLog.at[ii,'condition'] = self.cond
        dataLog.at[ii,'trigger'] = self.trigger
        dataLog.at[ii,'response'] = self.response
        dataLog.at[ii,'rt(ms)'] = self.rt


# =======================================================================           
# present rating setup and capture response
def presentRating(screen,  screenColor, ratimImg, ratingRect, ratingDur, mCal):
    # input variables:
    # screen: handle to pygame screen object
    # screenColor: screen color tuple: (R,G,B)
    # ratingImg: picture of rating setup
    # ratingRect: rectangle defining valence/arousal borders
    # ratingDur: float duration of rating period
    # mCal: dict of mouse calibration values
    val= np.nan
    aro = np.nan
    rt = -1
    # show rating  ------------------------------------
    screen.blit(ratingImg, ratingRect)
    pygame.display.update()

    ratingStart = datetime.now()
    while (datetime.now() - ratingStart).seconds * 1000 < ratingDur:
        # set time
        t = (datetime.now() - ratingStart).seconds * 1000 + round((datetime.now() - ratingStart).microseconds/1000)
  
        # wait for user choice
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                response = f"M{event.button}"                 
                pos = event.pos
                
                val = (pos[0] - mCal["center"][0]) / (abs(mCal["left"] - mCal["right"])/2)
                aro = (mCal["center"][1] - pos[1]) / (abs(mCal["top"] - mCal["bottom"])/2)
        
                if (val > -1 and val < 1) and (aro > -1 and aro < 1):
                    # get LAST click time
                    rt = t
                    # mark LAST choice
                    screen.blit(ratingImg, ratingRect)
                    pygame.draw.circle(screen, (100,100,100),pos,5)
                    pygame.display.update()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return -100,0,0

    return val, aro, rt
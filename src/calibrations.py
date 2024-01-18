# =======================================================================
# mouse response area calibration

def mouseCalibration(screen, screenSize, screenColor, screenCenter, calib):
    # input variables
    # screen: handle to pygame screen object
    # screenSize: screen size tuple: (width, height)
    # screenColor: screen color tuple: (R,G,B)
    # screenCenter: tuple of logical screen center (x,y)
    # calib: list of calibration pictures
    while True:
        mC = []
        mouseCalib = {}
        for ii in range(len(calib)-1):
            ons, resp, rt, pos = calib[ii].present(screen,screenSize,screenColor, True)
            mC.append(pos)

        # estimate values and draw rectangle
        mouseCalib['left']   = round((mC[0][0] + mC[3][0])/2)
        mouseCalib['right']  = round((mC[1][0] + mC[2][0])/2)
        mouseCalib['top']    = round((mC[0][1] + mC[1][1])/2)
        mouseCalib['bottom'] = round((mC[2][1] + mC[3][1])/2)
        mouseCalib['center'] = (mouseCalib['left'] + (round(abs(mouseCalib['right']-mouseCalib['left'])/2)),\
                                mouseCalib['top'] + (round(abs(mouseCalib['bottom']-mouseCalib['top'])/2)))

        # check calibration quality
        # if ok, return calibration values
        if calibrationOK(screenCenter, mouseCalib, 2) == True:
            return mouseCalib
        # if not: repeat
        else:
            # show calibration results ------------------------------------
            img = pygame.image.load(calib[-1].stimContent)
            img = pygame.transform.scale(img, (calib[-1].size[0], calib[-1].size[1]))                  
            img.convert()
            rect = img.get_rect()
            rect.center = ((calib[-1].pos[0], calib[-1].pos[1]))
            screen.blit(img, rect)
            pygame.draw.rect(screen, (0,255,0),\
                        (mouseCalib['left'],mouseCalib['top'],\
                        abs(mouseCalib['right']-mouseCalib['left']),\
                        abs(mouseCalib['bottom']-mouseCalib['top'])),width = 1)
            pygame.draw.line(screen, (0,255,0),(mouseCalib['left'],mouseCalib['bottom']),\
                        (mouseCalib['right'],mouseCalib['top']))
            pygame.draw.line(screen, (0,255,0),(mouseCalib['right'],mouseCalib['bottom']),\
                        (mouseCalib['left'],mouseCalib['top']))
            pygame.draw.circle(screen, (0,255,0),mouseCalib['center'],20,width = 1)
            
            pygame.display.update()
            pygame.time.wait(1000)
            
            proceed = False
            while not proceed:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        proceed = True
                        

# =======================================================================
def eyetrackerCalibration(screen, screenSize, screenColor, screenCenter, calib):
    # input variables
    # screen: handle to pygame screen object
    # screenSize: screen size tuple: (width, height)
    # screenColor: screen color tuple: (R,G,B)
    # screenCenter: tuple of logical screen center (x,y)
    # calib: list of calibration pictures
    calib[0].present(screen,screenSize,screenColor, True)
    for ii in range(1,len(calib)):
        calib[ii].present(screen,screenSize,screenColor, False)


# =======================================================================           
# check calibration quality
def calibrationOK(sC, mC, tolPix):
    # input variables
    # sC = screen center
    # mC = mouse calibration dict whith "left","right","bottom","top" and "center"
    # tolPix = tolerance in pixels
    width = abs(mC['left']-mC['right'])
    height = abs(mC['bottom']-mC['top'])
    centX = mC['left'] + round(width/2)
    centY = mC['top']  + round(height/2)
    print('\nCalibration results:')
    print(f'Square asymmetry (pix): {abs(height-width)}')
    print(f'Center misfit x,y (pix): {abs(centX-sC[0])}, {abs(centY-sC[1])}')
    
    if  abs(height-width) > tolPix or abs(centX-sC[0]) > tolPix or abs(centY-sC[1]) > tolPix:
        return False
    else:
        return True
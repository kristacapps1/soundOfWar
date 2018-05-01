import time,sys,math,random
import RPi.GPIO as GPIO
#import Adafruit_MCP4725

class game :
    def __init__(self):
        self.roundNum = 0
        self.gameMode = 1
        self.modePin = 10
        self.buttonPressed = 0
        self.maxRounds = 3
        self.pOneScore = 0
        self.pTwoScore = 0
        self.pOneVol = 0
        self.pTwoVol = 0
        self.count = 5
        
    def setup(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        
        #Setup mode Button
        GPIO.setup(self.modePin, GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.modePin,GPIO.FALLING,callback=self.changeMode,bouncetime=200)
        
        #Setup LEDs
        
        #Setup Speakers
        
        #Setup Motors
    
    def changeMode(self):
        if(self.gameMode == 0):
            self.gameMode = 1
        else :
            self.gameMode = 0
    
    def dispCount(self):
        if(self.count == 0):
            ##do two middle LEDs
            # xxxxooxxxx
            # xxxxooxxxx
            pass
        elif(self.count == 1):
            ##do next to two middle LEDs
            # xxxoxxoxxx
            # xxxoxxoxxx
            pass
        elif(self.count == 2):
            ##do next outer LEDs
            # xxoxxxxoxx
            # xxoxxxxoxx
            pass
        elif(self.count == 3):
            ##do next outer LEDs
            # xoxxxxxxox
            # xoxxxxxxox
            pass
        elif(self.count == 4):
            ##do next outer LEDs
            # oxxxxxxxxo
            # oxxxxxxxxo
            pass
        else:
            pass
    
    def doRound(self) :
        self.readSound()
        avgPone = self.pOneVol
        avgPtwo = self.pTwoVol
        while(self.count > 0):
            self.readSound()
            avgPone = (self.pOneVol+avgPone)/2
            avgPtwo = (self.pTwoVol+avgPtwo)/2
            self.count = self.count -1
            self.dispCount()
            time.sleep(1)
        self.moveCart(avgPone,avgPtwo)
        
    def runSuddenDeath(self):
        self.count = 30
        while(self.count>0):
            self.readSound()
            self.moveCart(self.pOneVol,self.pTwoVol)
            if(self.count%10 == 0):
                tmpCount = self.count
                self.count = self.count/10
                self.dispCount()
                self.count = tmpCount
            self.count = self.count -1
        
    def readSound(self):
        # temporary value generator
        self.pOneVol = random.randint(1,100)
        self.pTwoVol = random.randint(1,100)
    
    def dispWinner(self):
        # display winner with LEDs
        tmpCount = 0
        while(tmpCount < 3):
            if(self.pOneScore > self.pTwoScore):
                ## disp all right side LEDs
                print("Player 1 wins!")
            elif(self.pOneScore < self.pTwoScore):
                ## disp all left side LEDs
                print("player 2 wins!")
            else:
                ## disp all LEDs
                print("its a tie!")
            tmpCount = tmpCount + 1
            time.sleep(1)
    
    def moveCart(self,avgPone,avgPtwo):
        if(avgPone<avgPtwo):
            movement = avgPtwo - avgPone
            print("cart moves towards player two by {}",movement)
            self.pTwoScore = self.pTwoScore + movement
        elif(avgPone>avgPtwo):
            movement = avgPone - avgPtwo
            print("cart moves towards player one by {}",movement)
            self.pOneScore = self.pOneScore + movement
        else:
            movement = 0
            print("cart doesn't move!")
        
    def runGame(self) :
        if(self.gameMode == 0):
            while(self.roundNum < self.maxRounds):
                self.doRound()
                self.roundNum = self.roundNum + 1
                self.count = 5
        elif(self.gameMode == 1):
            self.runSuddenDeath()
        else:
            pass
        self.roundNum = 0
        self.dispWinner()
            
## Run Sound of War            
new_game = game()
new_game.setup()

while(True):
    new_game.runGame()
    
## end program
        
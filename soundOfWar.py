import time,sys,math,random
import RPi.GPIO as GPIO
#import Adafruit_MCP4725
sys.path.append('/home/pi/CSCE462/Lab05/Adafruit_Python_MCP3008')
sys.path.append('/usr/local/lib/python2.7/dist-packages')
import Adafruit_MCP3008
import Adafruit_GPIO.SPI as SPI
import RPi.GPIO as GPIO
from pygame import mixer

class game :
    def __init__(self):
        self.roundNum = 0
        self.gameMode = 0
        self.modePin = 4
        self.buttonPressed = 0
        self.CLK = 11
        self.MISO =9
        self.MOSI =10
        self.CS = 8
        self.mcp = Adafruit_MCP3008.MCP3008(clk=self.CLK,cs=self.CS,miso=self.MISO,mosi=self.MOSI)
        self.maxRounds = 3
        self.pOneScore = 0
        self.pTwoScore = 0
        self.pOneVol = 0
        self.pTwoVol = 0
        self.invertRound=0
        self.count = 5
        self.lights=[25,12,24,23,21,20,16]
        self.motors=[13,26,22,27]
        self.song=["02 - We Are The Champions.mp3"]
        self.roundCount=[0,0]
        
    def setup(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        
        #Setup mode Button
        GPIO.setup(self.modePin, GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.modePin,GPIO.FALLING,callback=self.changeMode,bouncetime=200)
        
        #Setup LEDs
        for i in range(0,7):
            GPIO.setup(self.lights[i], GPIO.OUT)
        
        #Setup Speakers
        mixer.init()
        mixer.music.load(self.song[0])
        
        #Setup Motors
        for i in range(0,4):
            GPIO.setup(self.motors[i],GPIO.OUT)
    
    def changeMode(self):
        if(self.gameMode == 0):
            self.gameMode = 1
        else :
            self.gameMode = 0
    
    def dispCount(self):
        if(self.count == 0):
            ##do middle LEDs
            # xxxxoxxxx
            # xxxxoxxxx
            GPIO.output(self.lights[3],GPIO.HIGH)
            
        elif(self.count == 1):
            ##do next to two middle LEDs
            # xxxoxoxxx
            # xxxoxoxxx
            GPIO.output(self.lights[2],GPIO.HIGH)
            GPIO.output(self.lights[4],GPIO.HIGH)
            
        elif(self.count == 2):
            ##do next outer LEDs
            # xxoxxxoxx
            # xxoxxxoxx
            GPIO.output(self.lights[1],GPIO.HIGH)
            GPIO.output(self.lights[5],GPIO.HIGH)
            
        elif(self.count == 3):
            ##do next outer LEDs
            # xoxxxxxox
            # xoxxxxxox
            GPIO.output(self.lights[0],GPIO.HIGH)
            GPIO.output(self.lights[6],GPIO.HIGH)
            
        elif(self.count == 4):
            ##do next outer LEDs
            # oxxxxxxxo
            # oxxxxxxxo
            for i in range(7,0):
                if(i==4):
                    GPIO.output(self.lights[4],GPIO.HIGH)
                else:
                    GPIO.output(self.lights[i],GPIO.HIGH)
                    GPIO.output(self.lights[7-i],GPIO.HIGH)
                time.sleep(.5)
                
        else:
            pass
        
    def switch_leds(self):
        for j in range(0,8):
            for i in range(0,7):
                #print(i)
                GPIO.output(self.lights[i],GPIO.HIGH)
                time.sleep(.05)
            for i in range(0,7):
                GPIO.output(self.lights[i],GPIO.LOW)
            for k in range(0,7):
                #print(6-k)
                GPIO.output(self.lights[6-k],GPIO.HIGH)
                time.sleep(.05)
            for i in range(0,7):
                GPIO.output(self.lights[i],GPIO.LOW)
        
    def sudden_leds(self):
        for j in range(0,8):
            for i in [0,2,4,6]:
                #print(i)
                GPIO.output(self.lights[i],GPIO.HIGH)
            time.sleep(0.5)
            for i in range(0,7):
                GPIO.output(self.lights[i],GPIO.LOW)
            for i in [1,3,5]:
                #print(i)
                GPIO.output(self.lights[i],GPIO.HIGH)
            time.sleep(0.5)
            for i in range(0,7):
                GPIO.output(self.lights[i],GPIO.LOW)
            
    
    def doRound(self) :
        self.readSound()
        avgPone = self.pOneVol
        avgPtwo = self.pTwoVol
        while(self.count > 0):
            self.readSound()
            if self.pOneVol>600:
                avgPone = (self.pOneVol+avgPone)/2
            if self.pTwoVol>600:
                avgPtwo = (self.pTwoVol+avgPtwo)/2
            self.count = self.count -1
            self.dispCount()
            time.sleep(1)
            self.reset_leds()
        self.moveCart(avgPone,avgPtwo)
        
    def runSuddenDeath(self):
        self.count = 30
        p2score = 0
        p1score = 0
        while(self.count>0):
            self.readSound()
            self.moveCart(self.pOneVol,self.pTwoVol)
            if(self.count%10 == 0):
                tmpCount = self.count
                self.count = self.count/10
                self.dispCount()
                self.count = tmpCount
            self.count = self.count-1
        
    def readSound(self):
        # temporary value generator
        self.pOneVol = self.mcp.read_adc(1)
        self.pTwoVol = self.mcp.read_adc(3)
        
    def reset_leds(self):
        for i in range(0,7):
            GPIO.output(self.lights[i],GPIO.LOW)
    
    def dispWinner(self):
        # display winner with LEDs
        tmpCount = 0
        while(tmpCount < 3):
            if(self.roundCount[0] > self.roundCount[1]):
                ## disp all right side LEDs
                print("Player 1 wins!")
                for i in range(4,7):
                    GPIO.output(self.lights[i],GPIO.HIGH)
                time.sleep(3)
                self.reset_leds()
            elif(self.roundCount[0] < self.roundCount[1]):
                ## disp all left side LEDs
                print("player 2 wins!")
                for i in range(0,4):
                    GPIO.output(self.lights[i],GPIO.HIGH)
                time.sleep(3)
                self.reset_leds()
            else:
                ## disp all LEDs
                print("its a tie!")
            tmpCount = tmpCount + 1
            time.sleep(1)
    
    def moveCart(self,avgPone,avgPtwo):
        print(avgPone)
        print(avgPtwo)
        if(avgPone<avgPtwo):
            movement = avgPtwo - avgPone
            movement=movement+5
            if(self.invertRound ==2):
                movement = 9
            print("cart moves towards player two by {}",movement)
            pnumber=2
            self.pTwoScore = self.pTwoScore + movement
            if(self.invertRound == 1):
                self.roundCount[1]=self.roundCount[1]-1
                pnumber=1
            else:
                self.roundCount[1]=self.roundCount[1]+1
            for j in range(0,2):
                for i in range(0,4):
                        GPIO.output(self.lights[i],GPIO.HIGH)
                        time.sleep(.1)
                self.reset_leds()
        elif(avgPone>avgPtwo):
            movement = avgPone - avgPtwo
            movement = movement+5
            if(self.invertRound ==2):
                movement = 9
            print("cart moves towards player one by {}",movement)
            pnumber=1
            self.pOneScore = self.pOneScore + movement
            if(self.invertRound == 1):
                self.roundCount[0]=self.roundCount[0]-1
                pnumber=2
            else:
                self.roundCount[0]=self.roundCount[0]+1
            
            for j in range(0,2):
                for i in range(4,7):
                        GPIO.output(self.lights[i],GPIO.HIGH)
                        time.sleep(.1)    
                self.reset_leds()
        else:
            movement = 0
            pnumber = 0
            print("cart doesn't move!")
        if(movement >30):
            movement = 30
        self.turnMotor(movement,pnumber)
        if(self.invertRound!=2):
            time.sleep(5)
        
    def turnMotor(self,movement,pnumber) :
        tmpMotor = pnumber - 1 
        while(movement>0) :
            print(movement)
            print(pnumber)
            if(pnumber == 2):
                self.goRight()
            if(pnumber == 1):
                self.goLeft()
            movement = movement -10
        
    def goRight(self):
        print("going right ")
        GPIO.output(self.motors[3],GPIO.HIGH)
        time.sleep(0.3)
        GPIO.output(self.motors[3],GPIO.LOW)
        time.sleep(0.5)
        GPIO.output(self.motors[2],GPIO.HIGH)
        time.sleep(0.3)
        GPIO.output(self.motors[2],GPIO.LOW)
        time.sleep(0.5)
        
    def goLeft(self):
        print("going left")
        GPIO.output(self.motors[0],GPIO.HIGH)
        time.sleep(0.3)
        GPIO.output(self.motors[0],GPIO.LOW)
        time.sleep(0.5)
        GPIO.output(self.motors[1],GPIO.HIGH)
        time.sleep(0.3)
        GPIO.output(self.motors[1],GPIO.LOW)
        time.sleep(0.5)
            
        
    def runGame(self) :
        if(self.gameMode == 0):
            mixer.init()
            mixer.music.load("02 - We Are The Champions.mp3")
            mixer.music.play()
            time.sleep(7)
            while(self.roundNum < self.maxRounds):
                # Decide round type
                tmprand = random.randint(1,101)
                print(tmprand)
                if(tmprand >80):
                    self.invertRound = 1
                    self.switch_leds()
                elif(tmprand < 0) :
                    self.invertRound = 2
                    self.sudden_leds()
                else:
                    self.invertRound = 0
                if(self.invertRound!=2):
                    self.doRound()
                else :
                    self.runSuddenDeath()
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
        

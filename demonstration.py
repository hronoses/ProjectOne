# -*- encoding: UTF-8 -*-

import sys
import motion
import time
from naoqi import ALProxy

def Stiffness(proxy, value=1):
    pNames = "Body"
    pStiffnessLists = value
    pTimeLists = 1.0
    proxy.stiffnessInterpolation(pNames, pStiffnessLists, pTimeLists)

def main(robotIP):
    # Init proxies.
    try:
        motionProxy = ALProxy("ALMotion", robotIP, 9559)
    except Exception, e:
        print "Could not create proxy to ALMotion"
        print "Error was: ", e

    try:
        postureProxy = ALProxy("ALRobotPosture", robotIP, 9559)
    except Exception, e:
        print "Could not create proxy to ALRobotPosture"
        print "Error was: ", e

    try:
        aup = ALProxy("ALAudioPlayer", robotIP, 9559)
        aud = ALProxy("ALAudioDevice", robotIP, 9559)
    except Exception,e:
        print "Could not create proxy to ALAudioPlayer"
        print "Error was: ",e
        sys.exit(1)

    # Set NAO in Stiffness On
    Stiffness(motionProxy, 1)
    speed = 0.5
    postureProxy.goToPosture("Stand", speed)
    motionProxy.post.setAngles("HeadYaw", -0.9, 0.05)
    motionProxy.setAngles("HeadPitch", 0.2, 0.05)
    time.sleep(3)


    aud.setOutputVolume(60)
    ffile = "//home/nao/naoqi/wav/audio2_vocoder.wav"
    sound = aup.loadFile(ffile)
    aup.play(sound)

    time.sleep(4)
    motionProxy.setAngles("HeadYaw", 0, 0.3)
    postureProxy.goToPosture("Crouch", 0.5)
    Stiffness(motionProxy, 0)

if __name__ == "__main__":
    main("192.168.62.72")
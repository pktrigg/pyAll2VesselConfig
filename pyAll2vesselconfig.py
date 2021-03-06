import sys
sys.path.append("C:/development/Python/pyall")

import argparse
from datetime import datetime
import geodetic
from glob import glob
import pyall
import time
import os.path
import warnings
from xml.etree.ElementTree import Element, SubElement, Comment, ElementTree
from xml.etree import ElementTree
from xml.dom import minidom

def main():
    parser = argparse.ArgumentParser(description='Read Kongsberg ALL file and create a caris hvf vessel config file.')
    parser.add_argument('-i', dest='inputFile', action='store', help='-i <ALLfilename> : input ALL filename to image. It can also be a wildcard, e.g. *.all')

    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    # we need to remember the previous record so we only create uniq values, not duplicates
    prevNav1Params = {}
    prevPitchParams = ""
    prevRollParams = ""
    prevHeaveParams = ""
    prevGyroParams = ""
    prevWaterlineParams = ""
    prevDepthParams = ""

    fileCounter=0
    print ("processing with settings: ", args)
    root = createHVFRoot(datetime.now())

    for filename in glob(args.inputFile):
        r = pyall.ALLReader(filename)
        start_time = time.time() # time  the process
        InstallationRecordCount = 0
        while r.moreData():
            # read a datagram.  If we support it, return the datagram type and aclass for that datagram
            # The user then needs to call the read() method for the class to undertake a fileread and binary decode.  This keeps the read super quick.
            TypeOfDatagram, datagram = r.readDatagram()

            if TypeOfDatagram == 'I':
                datagram.read()
                # print (datagram.installationParameters)
                
                root, prevNav1Params = createNavSensor(root, r.currentRecordDateTime(), datagram.installationParameters, prevNav1Params)
                root, prevGyroParams = createGyroSensor(root, r.currentRecordDateTime(), datagram.installationParameters, prevGyroParams)
                root, prevHeaveParams = createHeaveSensor(root, r.currentRecordDateTime(), datagram.installationParameters, prevHeaveParams)
                root, prevPitchParams = createPitchSensor(root, r.currentRecordDateTime(), datagram.installationParameters, prevPitchParams)
                root, prevRollParams = createRollSensor(root, r.currentRecordDateTime(), datagram.installationParameters, prevRollParams)
                root, prevWaterlineParams = createWaterlineSensor(root, r.currentRecordDateTime(), datagram.installationParameters, prevWaterlineParams)
                root, prevDepthParams = createDepthSensor(root, r.currentRecordDateTime(), datagram.installationParameters, prevDepthParams, datagram.EMModel, datagram.SerialNumber)

                InstallationRecordCount = InstallationRecordCount + 1
        update_progress("Processed file: %s InstallationRecords: %d" % (filename, InstallationRecordCount), (fileCounter/len(args.inputFile)))
        fileCounter +=1

    f = open('file.hvf', 'w')
    f.write(prettify (root))
    f.close()
    update_progress("Processed all files. InstallationRecords: %d" % (InstallationRecordCount), 1)

def createDepthSensor(root, datetime, installationParameters, prevParams, EMModel, serialNumber):
    installationRecordDateString = datetime.strftime("%Y-%j %H:%M:%S")
    startBeam = 1 # TODO - try automat this based on parameters in the .all file

    Sensor = SubElement(root, 'DepthSensor')
    TimeStamp = SubElement(Sensor, 'TimeStamp')
    TimeStamp.set('value', installationRecordDateString)
    Latency = SubElement(TimeStamp, 'Latency')
    Latency.set('value', '0.000')
    W = SubElement(TimeStamp, 'SensorClass')
    W.set('value', "Swath")
    C = SubElement(TimeStamp, 'Comment')
    C.set('value', "from S1,2,3 X,Y,Z fields in .all file)")

    # now do the transducers
    Trans = SubElement(TimeStamp, 'TransducerEntries')

    #taken from EM datagram manual I-Installation Note 19 Table which documents the S-field mapping to the models.
    if EMModel == 122 or \
       EMModel == 302 or \
       EMModel == 710:
        # S1 is Tx and S2 is Rx 
        newParams = {}
        newParams = {}
        newParams["X"] = installationParameters.get("S1X")
        newParams["Y"] = installationParameters.get("S1Y")
        newParams["Z"] = installationParameters.get("S1Z")
        newParams["H"] = installationParameters.get("S1H")
        newParams["P"] = installationParameters.get("S1P")
        newParams["R"] = installationParameters.get("S1R")
        createTransducer1(Trans, 1, EMModel, serialNumber, startBeam, newParams)

        newParams = {}
        newParams["X"] = installationParameters.get("S2X")
        newParams["Y"] = installationParameters.get("S2Y")
        newParams["Z"] = installationParameters.get("S2Z")
        newParams["H"] = installationParameters.get("S2H")
        newParams["P"] = installationParameters.get("S2P")
        newParams["R"] = installationParameters.get("S2R")
        createTransducer1(Trans, 2, EMModel, serialNumber, startBeam, newParams)

    if EMModel == 2040:  
        # S1 is Tx and S2 is Rx 
        newParams = {}
        newParams["X"] = installationParameters.get("S1X")
        newParams["Y"] = installationParameters.get("S1Y")
        newParams["Z"] = installationParameters.get("S1Z")
        newParams["H"] = installationParameters.get("S1H")
        newParams["P"] = installationParameters.get("S1P")
        newParams["R"] = installationParameters.get("S1R")
        createTransducer1(Trans, 1, EMModel, serialNumber, startBeam, newParams, "Tx from S1X,Y,Z installation datagram")

        newParams = {}
        newParams["X"] = installationParameters.get("S2X")
        newParams["Y"] = installationParameters.get("S2Y")
        newParams["Z"] = installationParameters.get("S2Z")
        newParams["H"] = installationParameters.get("S2H")
        newParams["P"] = installationParameters.get("S2P")
        newParams["R"] = installationParameters.get("S2R")
        createTransducer1(Trans, 2, EMModel, serialNumber, startBeam, newParams, "Rx from S2X,Y,Z installation datagram")


    #TODO need to figure out how to identify dial head system! pkpk
    #we can test for GO1 and GO2 which are the gain offsets for transducer 1 and 2.  If GO2 exists, we have a dual header
    if EMModel == 2040 and "GO2" in installationParameters:
       # S1 is Tx and S2 is Rx 
        newParams = {}

    # EM 3002 and EM2040C
    if EMModel == 3020 or \
       EMModel == 2045:
       # S1 is SonarHead1 and S2 is SonarHead2
        newParams = {}



    newParams = {}
    newParams["S3X"] = installationParameters.get("S3X")
    newParams["S3Y"] = installationParameters.get("S3Y")
    newParams["S3Z"] = installationParameters.get("S3Z")
    newParams["S3H"] = installationParameters.get("S3H")
    newParams["S3P"] = installationParameters.get("S3P")
    newParams["S3R"] = installationParameters.get("S3R")

    return root, newParams

def createTransducer1(Trans, ID, EMModel, serialNumber, startBeam, newParams, Comment):

    Transducer = SubElement(Trans, 'Transducer')
    Transducer.set('Number', str(ID))
    Transducer.set('StartBeam', "1")
    Transducer.set('Model', getSimradCode(EMModel))

    Offsets = SubElement(Transducer, 'Offsets')
    Offsets.set('X', newParams["X"])
    Offsets.set('Y', newParams["Y"])
    Offsets.set('Z', newParams["Z"])
    Offsets.set('Latency', "0.000")

    Mount = SubElement(Transducer, 'MountAngle')
    Mount.set('Pitch', newParams["P"])
    Mount.set('Roll', newParams["R"])
    Mount.set('Azimuth', newParams["H"])

    C1 = SubElement(Transducer, 'Manufacturer')
    C1.set('value', "pyAllVesselConfig")
    C3 = SubElement(Transducer, 'SerialNumber')
    C3.set('value', str(serialNumber))
    Com = SubElement(Transducer, 'Comment')
    Com.set('value', Comment)

    return Trans

def createWaterlineSensor(root, datetime, installationParameters, prevParams):
    installationRecordDateString = datetime.strftime("%Y-%j %H:%M:%S")
    newParams = {}
    newParams["WLZ"] = installationParameters.get("WLZ")

    # if (set(prevParams) == set(newParams):
    Sensor = SubElement(root, 'WaterlineHeight')
    TimeStamp = SubElement(Sensor, 'TimeStamp')
    TimeStamp.set('value', installationRecordDateString)
    Latency = SubElement(TimeStamp, 'Latency')
    Latency.set('value', '0.000')
    W = SubElement(TimeStamp, 'Waterline')
    W.set('value', newParams["WLZ"])

    ApplyFlag = SubElement(TimeStamp, 'ApplyFlag')
    ApplyFlag.set('value', 'No')

    W = SubElement(TimeStamp, 'StdDev')
    W.set('Waterline', '0.000')

    C = SubElement(TimeStamp, 'Comment')
    C.set('value', "from WLZ waterline field")

    return root, newParams

def createRollSensor(root, datetime, installationParameters, prevParams):
    installationRecordDateString = datetime.strftime("%Y-%j %H:%M:%S")
    newParams = {}
    newParams["MSR"] = installationParameters.get("MSR")

    # if (set(prevParams) == set(newParams):
    Sensor = SubElement(root, 'RollSensor')
    TimeStamp = SubElement(Sensor, 'TimeStamp')
    TimeStamp.set('value', installationRecordDateString)
    Latency = SubElement(TimeStamp, 'Latency')
    Latency.set('value', '0.000')
    ApplyFlag = SubElement(TimeStamp, 'ApplyFlag')
    ApplyFlag.set('value', 'No')

    Offsets = SubElement(TimeStamp, 'Offsets')
    E = SubElement(Offsets, 'Entry')
    E.set('Roll', newParams["MSR"])
    
    C = SubElement(TimeStamp, 'Comment')
    C.set('value', "from MSR field (motion system 1)")

    C = SubElement(TimeStamp, 'Manufacturer')
    C.set('value', "pyAllVesselConfig")

    C = SubElement(TimeStamp, 'Model')
    C.set('value', "(null)")

    C = SubElement(TimeStamp, 'SerialNumber')
    C.set('value', "(null)")

    return root, newParams

def createPitchSensor(root, datetime, installationParameters, prevParams):
    installationRecordDateString = datetime.strftime("%Y-%j %H:%M:%S")
    newParams = {}
    newParams["MSP"] = installationParameters.get("MSP")

    # if (set(prevParams) == set(newParams):
    Sensor = SubElement(root, 'PitchSensor')
    TimeStamp = SubElement(Sensor, 'TimeStamp')
    TimeStamp.set('value', installationRecordDateString)
    Latency = SubElement(TimeStamp, 'Latency')
    Latency.set('value', '0.000')
    ApplyFlag = SubElement(TimeStamp, 'ApplyFlag')
    ApplyFlag.set('value', 'No')

    Offsets = SubElement(TimeStamp, 'Offsets')
    E = SubElement(Offsets, 'Entry')
    E.set('Pitch', newParams["MSP"])
    
    C = SubElement(TimeStamp, 'Comment')
    C.set('value', "from MSP field (motion system 1)")

    C = SubElement(TimeStamp, 'Manufacturer')
    C.set('value', "pyAllVesselConfig")

    C = SubElement(TimeStamp, 'Model')
    C.set('value', "(null)")

    C = SubElement(TimeStamp, 'SerialNumber')
    C.set('value', "(null)")

    return root, newParams

def createGyroSensor(root, datetime, installationParameters, prevParams):
    installationRecordDateString = datetime.strftime("%Y-%j %H:%M:%S")
    newParams = {}
    newParams["GCG"] = installationParameters.get("GCG")

    # if (set(prevParams) == set(newParams):
    Sensor = SubElement(root, 'GyroSensor')
    TimeStamp = SubElement(Sensor, 'TimeStamp')
    TimeStamp.set('value', installationRecordDateString)
    Latency = SubElement(TimeStamp, 'Latency')
    Latency.set('value', '0.000')
    ApplyFlag = SubElement(TimeStamp, 'ApplyFlag')
    ApplyFlag.set('value', 'No')

    Offsets = SubElement(TimeStamp, 'Offsets')

    Gyro = SubElement(Offsets, 'Gyro')
    E = SubElement(Gyro, 'Entry')
    E.set('Azimuth', newParams["GCG"])
    E.set('Offset', "0.000")

    C = SubElement(TimeStamp, 'Comment')
    C.set('value', "from GCG field")

    C = SubElement(TimeStamp, 'Manufacturer')
    C.set('value', "pyAllVesselConfig")

    C = SubElement(TimeStamp, 'Model')
    C.set('value', "(null)")

    C = SubElement(TimeStamp, 'SerialNumber')
    C.set('value', "(null)")

    return root, newParams

def createHeaveSensor(root, datetime, installationParameters, prevParams):
    installationRecordDateString = datetime.strftime("%Y-%j %H:%M:%S")
    newParams = {}
    newParams["MSX"] = installationParameters.get("MSX")
    newParams["MSY"] = installationParameters.get("MSY")
    newParams["MSZ"] = installationParameters.get("MSZ")

    # if (set(prevParams) == set(newParams):
    Sensor = SubElement(root, 'HeaveSensor')
    TimeStamp = SubElement(Sensor, 'TimeStamp')
    TimeStamp.set('value', installationRecordDateString)
    Latency = SubElement(TimeStamp, 'Latency')
    Latency.set('value', '0.000')
    ApplyFlag = SubElement(TimeStamp, 'ApplyFlag')
    ApplyFlag.set('value', 'No')

    Offsets = SubElement(TimeStamp, 'Offsets')
    E = SubElement(Offsets, 'Entry')
    E.set('X', newParams["MSX"])
    E.set('Y', newParams["MSY"])
    E.set('Z', newParams["MSZ"])
    E.set('Heave', "0.000")
    
    C = SubElement(TimeStamp, 'Comment')
    C.set('value', "from MSX, MSY, MSP fields")

    C = SubElement(TimeStamp, 'Manufacturer')
    C.set('value', "pyAllVesselConfig")

    C = SubElement(TimeStamp, 'Model')
    C.set('value', "(null)")

    C = SubElement(TimeStamp, 'SerialNumber')
    C.set('value', "(null)")

    return root, newParams

def createNavSensor(root, datetime, installationParameters, prevNav1Params):
    installationRecordDateString = datetime.strftime("%Y-%j %H:%M:%S")
    Nav1Params = {}
    Nav1Params["P1X"] = installationParameters.get("P1X")
    Nav1Params["P1Y"] = installationParameters.get("P1Y")
    Nav1Params["P1Z"] = installationParameters.get("P1Z")

    # if (set(prevNav1Params) == set(Nav1Params):
    NavSensor = SubElement(root, 'NavSensor')
    TimeStamp = SubElement(NavSensor, 'TimeStamp')
    TimeStamp.set('value', installationRecordDateString)
    Latency = SubElement(TimeStamp, 'Latency')
    Latency.set('value', '0.000')
    Ellipse = SubElement(TimeStamp, 'Ellipse')
    Ellipse.set('value', 'WGS84')
    Offsets = SubElement(TimeStamp, 'Offsets')
    Offsets.set('X', Nav1Params["P1X"])
    Offsets.set('Y', Nav1Params["P1Y"])
    Offsets.set('Z', Nav1Params["P1Y"])

    C = SubElement(TimeStamp, 'Comment')
    C.set('value', "from P1X, P1Y, P1Z field")

    C = SubElement(TimeStamp, 'Manufacturer')
    C.set('value', "pyAllVesselConfig")

    C = SubElement(TimeStamp, 'Model')
    C.set('value', "(null)")

    C = SubElement(TimeStamp, 'SerialNumber')
    C.set('value', "(null)")

    return root, Nav1Params

def createHVFRoot(datetime):
    print ("Creating HVF file...")
    installationRecordDateString = datetime.strftime("%Y-%j %H:%M:%S")
    root = Element('HIPSVesselConfig')
    root.set('Version', '2.0')
    comment = Comment('Generated by pyAllVesselConfig' + installationRecordDateString)
    root.append(comment)
    v = SubElement(root, 'VesselShape')
    PL = SubElement(v, 'PlanCoordinates')

    E = SubElement(PL, 'Entry')
    E.set('X', '-2.000')
    E.set('Y', '0.000')

    E = SubElement(PL, 'Entry')
    E.set('X', '2.000')
    E.set('Y', '0.000')

    E = SubElement(PL, 'Entry')
    E.set('X', '2.000')
    E.set('Y', '10.000')

    E = SubElement(PL, 'Entry')
    E.set('X', '0.000')
    E.set('Y', '15.000')

    E = SubElement(PL, 'Entry')
    E.set('X', '-2.000')
    E.set('Y', '10.000')

    E = SubElement(PL, 'Entry')
    E.set('X', '-2.000')
    E.set('Y', '0.000')
    
    PR = SubElement(v, 'ProfileCoordinates')

    E = SubElement(PR, 'Entry')
    E.set('Y', '0.000')
    E.set('Z', '1.300')

    E = SubElement(PR, 'Entry')
    E.set('Y', '0.000')
    E.set('Z', '-1.700')

    E = SubElement(PR, 'Entry')
    E.set('Y', '10.000')
    E.set('Z', '-1.7000')

    E = SubElement(PR, 'Entry')
    E.set('Y', '15.000')
    E.set('Z', '1.300')

    E = SubElement(PR, 'Entry')
    E.set('Y', '0.000')
    E.set('Z', '1.300')

    RP = SubElement(v, 'RP')
    RP.set('Length', '0.000')
    RP.set('Width', '0.000')
    RP.set('Height', '0.000')
    
    return root

def writeHVFFile():

    GyroSensor = SubElement(root, 'GyroSensor')
    TimeStamp = SubElement(GyroSensor, 'TimeStamp')
    TimeStamp.set('value', installationRecordDateString)
    Latency = SubElement(TimeStamp, 'Latency')
    Latency.set('value', '0.000')
    ApplyFlag = SubElement(TimeStamp, 'ApplyFlag')
    Ellipse.set('value', 'No')

    HeaveSensor = SubElement(root, 'HeaveSensor')
    TimeStamp = SubElement(HeaveSensor, 'TimeStamp')
    TimeStamp.set('value', installationRecordDateString)
    Latency = SubElement(TimeStamp, 'Latency')
    Latency.set('value', '0.000')
    ApplyFlag = SubElement(TimeStamp, 'ApplyFlag')
    Ellipse.set('value', 'No')
    Offsets = SubElement(TimeStamp, 'Offsets')
    Offsets.set('X', '1.000')
    Offsets.set('Y', '2.000')
    Offsets.set('Z', '3.000')

    PitchSensor = SubElement(root, 'PitchSensor')
    TimeStamp = SubElement(PitchSensor, 'TimeStamp')
    TimeStamp.set('value', installationRecordDateString)
    Latency = SubElement(TimeStamp, 'Latency')
    Latency.set('value', '0.000')
    ApplyFlag = SubElement(TimeStamp, 'ApplyFlag')
    Ellipse.set('value', 'No')
    Offsets = SubElement(TimeStamp, 'Offsets')
    Offsets.set('Pitch', '1.000')

    RollSensor = SubElement(root, 'RollSensor')
    TimeStamp = SubElement(RollSensor, 'TimeStamp')
    TimeStamp.set('value', installationRecordDateString)
    Latency = SubElement(TimeStamp, 'Latency')
    Latency.set('value', '0.000')
    ApplyFlag = SubElement(TimeStamp, 'ApplyFlag')
    Ellipse.set('value', 'No')
    Offsets = SubElement(TimeStamp, 'Offsets')
    Offsets.set('Roll', '1.000')

    DepthSensor = SubElement(root, 'DepthSensor')
    TimeStamp = SubElement(DepthSensor, 'TimeStamp')
    TimeStamp.set('value', installationRecordDateString)
    Latency = SubElement(TimeStamp, 'Latency')
    Latency.set('value', '0.000')
    SensorClass = SubElement(TimeStamp, 'SensorClass')
    SensorClass.set('value', 'Swath')
    TransducerEntries = SubElement(TimeStamp, 'TransducerEntries')
    Transducer = SubElement(TransducerEntries, 'Transducer')
    Transducer.set('Number', '1')
    Transducer.set('Model', 'em2040_300N')
    Offsets = SubElement(Transducer, 'Offsets')
    Offsets.set('X', '1.000')
    Offsets.set('Y', '2.000')
    Offsets.set('Z', '3.000')
    Offsets.set('Latency', '4.000')

    MountAngle = SubElement(Transducer, 'MountAngle')
    Offsets.set('Pitch', '1.000')
    Offsets.set('Roll', '2.000')
    Offsets.set('Z', '3.000')
    Offsets.set('Azimuth', '4.000')

    ApplyFlag = SubElement(TimeStamp, 'ApplyFlag')
    Ellipse.set('value', 'No')
    Offsets = SubElement(TimeStamp, 'Offsets')
    Offsets.set('Roll', '1.000')

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def getSimradCode(EMModel):
    SimradCode = ""
    #   <SonarModel label="Simrad EM120" key="em120">
    if str(EMModel) == "3020":
        return "em3002"
    if str(EMModel) == "2040":
        return "em2040_200N"
    if EMModel == "302":
        return "em302"
    if EMModel == "122":
        return "em122"
    return SimradCode

def update_progress(job_title, progress):
    length = 20 # modify this to change the length
    block = int(round(length*progress))
    msg = "\r{0}: [{1}] {2}%".format(job_title, "#"*block + "-"*(length-block), round(progress*100, 2))
    if progress >= 1: msg += " DONE\r\n"
    sys.stdout.write(msg)
    sys.stdout.flush()

if __name__ == "__main__":
    main()


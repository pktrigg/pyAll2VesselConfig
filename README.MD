pyAll2vesselconfig
=====
* created:       November 2016
* by:            p.kennedy@fugro.com
* description:   python module to create a CARIS vessel config file from a Kongsberg .all file
* notes:         See main at end of script for example how to use this
* version 1.0
* developed for Python version 3.4 

Done
====
* Read the 'I' datagram from the .all file
* initial implementation
* test the .hvf file can be read by caris 
* confirmed resulting file can be read in caris 10
* Extract the installation offsets and angles from the I datagram


2Do
===
* Write the offsets to the HVF XML format suitable for CARIS
* add support for timestamps based on differences in the .all file.  This means we need to read the xml file and compare the results with each install record.  If they are different, we need to create a new record.
* we could make a mapping from the EMModel to the text strings in Caris here, but we would need more information. 

Example
-------

python pyall2vesselconfig.py
python pyall2vesselconfig.py -i <filename.all>  
python pyall2vesselconfig.py -i *.all  

output
------
'''
<?xml version="1.0"?>
<HIPSVesselConfig Version="2.0">
  <VesselShape>
    <PlanCoordinates>
      <Entry X="-2.000000" Y="-0.000000"/>
      <Entry X="2.000000" Y="-0.000000"/>
      <Entry X="2.000000" Y="6.000000"/>
      <Entry X="0.000000" Y="11.000000"/>
      <Entry X="-2.000000" Y="6.000000"/>
      <Entry X="-2.000000" Y="-0.000000"/>
    </PlanCoordinates>
    <ProfileCoordinates>
      <Entry Y="-0.000000" Z="1.300000"/>
      <Entry Y="-0.000000" Z="-1.700000"/>
      <Entry Y="6.000000" Z="-1.700000"/>
      <Entry Y="11.000000" Z="1.300000"/>
      <Entry Y="-0.000000" Z="1.300000"/>
    </ProfileCoordinates>
    <RP Length="0.000000" Width="2.000000" Height="1.700000"/>
  </VesselShape>
  <NavSensor>
    <TimeStamp value="2016-001 00:00:00">
      <Latency value="0.000000"/>
      <Ellipse value="WG84"/>
      <Offsets X="0.000000" Y="0.000000" Z="0.000000"/>
    </TimeStamp>
  </NavSensor>
  <GyroSensor>
    <TimeStamp value="2016-001 00:00:00">
      <Latency value="0.000000"/>
      <ApplyFlag value="No"/>
    </TimeStamp>
  </GyroSensor>
  <HeaveSensor>
    <TimeStamp value="2016-001 00:00:00">
      <Latency value="0.000000"/>
      <ApplyFlag value="No"/>
      <Offsets X="0.000000" Y="0.000000" Z="0.000000" Heave="0.000000"/>
      <Comment value="(null)"/>
      <Manufacturer value="(null)"/>
      <Model value="(null)"/>
      <SerialNumber value="(null)"/>
    </TimeStamp>
  </HeaveSensor>
  <PitchSensor>
    <TimeStamp value="2016-001 00:00:00">
      <Latency value="0.000000"/>
      <ApplyFlag value="No"/>
      <Offsets Pitch="0.000000"/>
      <Comment value="(null)"/>
      <Manufacturer value="(null)"/>
      <Model value="(null)"/>
      <SerialNumber value="(null)"/>
    </TimeStamp>
  </PitchSensor>
  <RollSensor>
    <TimeStamp value="2016-001 00:00:00">
      <Latency value="0.000000"/>
      <ApplyFlag value="No"/>
      <Offsets Roll="0.000000"/>
      <Comment value="(null)"/>
      <Manufacturer value="(null)"/>
      <Model value="(null)"/>
      <SerialNumber value="(null)"/>
    </TimeStamp>
  </RollSensor>
  <WaterlineHeight>
    <TimeStamp value="2016-247 00:00:00">
      <Latency value="0.000000"/>
      <WaterLine value="-0.880000"/>
      <ApplyFlag value="Yes"/>
      <StdDev Waterline="0.000000"/>
      <Comment value="(null)"/>
    </TimeStamp>
    <TimeStamp value="2016-252 00:00:00">
      <Comment value=""/>
      <Latency value="0.000000"/>
      <WaterLine value="-0.880000"/>
      <ApplyFlag value="Yes"/>
      <StdDev Waterline="0.000000"/>
    </TimeStamp>
  </WaterlineHeight>
  <SVPSensor>
    <TimeStamp value="2016-001 00:00:00">
      <Latency value="0.000000"/>
      <DualHead value="Yes"/>
      <Offsets X="-0.300000" Y="4.760000" Z="0.000000" X2="0.400000" Y2="4.770000" Z2="0.000000"/>
      <MountAngle Pitch="1.070000" Roll="24.230000" Azimuth="358.960000" Pitch2="1.070000" Roll2="-23.230000" Azimuth2="359.780000"/>
      <Comment value=""/>
    </TimeStamp>
  </SVPSensor>
  <DepthSensor>
    <TimeStamp value="2016-001 00:00:00">
      <Latency value="0.000000"/>
      <SensorClass value="Swath"/>
      <TransducerEntries>
        <Transducer Number="1" StartBeam="1" Model="em3002D">
          <Offsets X="-0.300000" Y="4.760000" Z="0.000000" Latency="0.000000"/>
          <MountAngle Pitch="0.000000" Roll="0.000000" Azimuth="-7.500000"/>
        </Transducer>
        <Transducer Number="2" StartBeam="255" Model="em3002">
          <Offsets X="0.400000" Y="4.770000" Z="0.000000" Latency="0.000000"/>
          <MountAngle Pitch="0.000000" Roll="0.000000" Azimuth="7.500000"/>
        </Transducer>
      </TransducerEntries>
    </TimeStamp>
  </DepthSensor>
</HIPSVesselConfig>

'''

help
----
```

```
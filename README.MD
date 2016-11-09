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


2Do
===
* initial implementation
* Read the 'I' datagram from the .all file
* Extract the installation offsets and angles from the I datagram
* Write the offsets to the HVF XML format suitable for CARIS
* test the .hvf file can be read by caris 
* add support for timestamps based on differences in the .all file.  This means we need to read the xml file and compare the results with each install record.  If they are different, we need to create a new record.

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
    <PlanCoordinates/>
    <ProfileCoordinates/>
    <RP Length="0.000000" Width="0.000000" Height="0.000000"/>
  </VesselShape>
  <NavSensor>
    <TimeStamp value="2016-001 00:00:00">
      <Latency value="0.000000"/>
      <Ellipse value="WG84"/>
      <Offsets X="0.000000" Y="0.000000" Z="0.000000"/>
    </TimeStamp>
  </NavSensor>
  and a whole lot more....
'''

help
----
```

```
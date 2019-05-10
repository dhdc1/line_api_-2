
from math import radians, sin, cos, acos

if __name__ == "__main__":

    point1 = [16.0123, 101.23566]  
    point2 = [15.325533, 100.14225]    
    
    slat = radians(point1[0])
    slon = radians(point1[1])
    elat = radians(point2[0])
    elon = radians(point2[1])

    dist = 6371.01 * acos(sin(slat)*sin(elat) + cos(slat)*cos(elat)*cos(slon - elon))
    print("The distance is %.2fkm." % dist)   

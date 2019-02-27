import numpy as np

def sin(angle_in_degrees):
    angle_in_radians = np.radians(angle_in_degrees)
    return np.sin(angle_in_radians)

def cos(angle_in_degrees):
    angle_in_radians = np.radians(angle_in_degrees)
    return np.cos(angle_in_radians)

def tan(angle_in_degrees):
    angle_in_radians = np.radians(angle_in_degrees)
    return np.tan(angle_in_radians)

def asin(len):
    return np.degrees(np.arcsin(len))

def acos(len):
    return np.degrees(np.arccos(len))

def atan(len):
    return np.degrees(np.arctan(len))

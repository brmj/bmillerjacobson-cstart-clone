#!/usr/bin/env python

__version__ = 1.0

from getopt import gnu_getopt, GetoptError
from math import exp, pi, sqrt
from os import mkdir
from os.path import exists
from sys import argv, exit

# Constants
g = 9.80665    # Gravitational acceleration
R = 8.31432    # Universal gas constant
M = 0.0289644    # Molar mass of Earth air
bulk = 1.42E5    # Bulk modulus of elasticity for dry air

class RocketSpecs:

    def __init__(self, t_B, T, m_E, m_F, m_P, A):
        self.t_B = t_B
        self.T = T
        self.m_E = m_E
        self.m_F = m_F
        self.m_P = m_P
        self.A = A

def barometric_formula(s, rho, L, T, h):
    if L == 0:
        return rho*exp((-1*g*M*(s-h))/(R*T))
    else:
        return rho*(T/(T+L*(s-h)))**((g*M)/(R*L)+1)

def rho(s):
    if 0 <= s < 11000:
        rho = 1.2250
        L = -0.0065
        T = 288.15
        h = 0
    elif 11000 <= s < 20000:
        rho = 0.36391
        L = 0.0
        T = 216.65
        h = 11000
    elif 20000 <= s < 32000:
        rho = 0.08803
        L = 0.001
        T = 216.65
        h = 20000
    elif 32000 <= s < 47000:
        rho = 0.01322
        L = 0.0028
        T = 228.65
        h = 32000
    elif 47000 <= s < 51000:
        rho = 0.00143
        L = 0.0
        T = 270.65
        h = 47000
    elif 51000 <= s < 71000:
        rho = 0.00086
        L = -0.0028
        T = 270.65
        h = 51000
    elif 71000 <= s < 86000:
        rho = 0.000064
        L = -0.002
        T = 214.65
        h = 71000
    else:
        return 0.000001

    rho = barometric_formula(s, rho, L, T, h)
    return rho

def rk_step(s, v, dsdt, dvdt, t, h):
    k1 = dsdt(s, v, t)
    k2 = dsdt(s+((h*k1)/2), v, t+h/2)
    k3 = dsdt(s+((h*k2)/2), v, t+h/2)
    k4 = dsdt(s+h*k3, v, t+h)
    s += (h/6)*(k1 + 2*k2 + 2*k3 + k4)

    k1 = dvdt(s, v, t)
    k2 = dvdt(s, v+((h*k1)/2), t+h/2)
    k3 = dvdt(s, v+((h*k2)/2), t+h/2)
    k4 = dvdt(s, v+h*k3, t+h)
    v += (h/6)*(k1 + 2*k2 + 2*k3 + k4)

    return s, v

def compute_stage(dirname, s_0, v_0, dsdt, dvdt, h, t_B):
    t = 0
    s = s_0
    v = v_0
    max_a = 0
    if dirname:
        fp_alt = open(dirname + "/altitude","w")
        fp_vel = open(dirname + "/velocity","w")
        fp_mach = open(dirname + "/mach","w")
        fp_acc = open(dirname + "/acceleration","w")
        fp_q = open(dirname + "/pressure","w")
    while t < t_B:
        s, v = rk_step(s, v, dsdt, dvdt, t, h)
        density = rho(s)
        speed_of_sound = sqrt(bulk / density)
        mach = v / speed_of_sound
        if dirname:
            fp_alt.write("%f, %f\n" % (t, s))
            fp_vel.write("%f, %f\n" % (t, v))
            fp_mach.write("%f, %f\n" % (t, mach))
            fp_acc.write("%f, %f\n" % (t, dvdt(s,v,t)))
            fp_q.write("%f, %f\n" % (t, density*v*v/2))
        t += h
    return t, s, v

def compute_zenith(dirname, t_0, s_0, v_0, dsdt, dvdt, h):
    t = t_0
    s = s_0
    v = v_0
    if dirname:
        fp_alt = open(dirname + "/altitude","a")
        fp_vel = open(dirname + "/velocity","a")
        fp_mach = open(dirname + "/mach","a")
        fp_acc = open(dirname + "/acceleration","a")
        fp_q = open(dirname + "/pressure","a")
    while v > 0:
        s, v = rk_step(s, v, dsdt, dvdt, t, h)
        density = rho(s)
        speed_of_sound = sqrt(bulk / density)
        mach = v / speed_of_sound
        if dirname:
            fp_alt.write("%f, %f\n" % (t, s))
            fp_vel.write("%f, %f\n" % (t, v))
            fp_mach.write("%f, %f\n" % (t, mach))
            fp_acc.write("%f, %f\n" % (t, dvdt(s,v,t)))
            fp_q.write("%f, %f\n" % (t, density*v*v/2))
        t += h
    return s, v

def get_drag(s, v):
    density = rho(s)
    speed_of_sound = sqrt(bulk / density)
    mach = v / speed_of_sound
    if mach <= 0.9 or mach > (0.41/0.21):
        drag_coeff = 0.15
    elif 0.9 < mach <= 1.0:
        drag_coeff = 0.15 + (0.26)*(mach-0.9)/0.1
    elif 1.0 < mach <= (0.41/0.21):
        drag_coeff = 0.41 - 0.21*(mach-1.0)
    return drag_coeff

def simulate_flight(dirname, specs):

    if dirname and not exists(dirname):
        mkdir(dirname)

    # Simulate engine burn
    def dsdt(s, v, t):
        return v

    def dvdt(s, v, t):
        mass = (specs.m_E + specs.m_P + (1-t/specs.t_B)*specs.m_F)
        drag = get_drag(s, v)
        return -1*g + (1/mass)*(specs.T - 0.5*rho(s)*drag*specs.A*v*v)

    t, s, v = compute_stage(dirname, 0, 0, dsdt, dvdt, 0.1, specs.t_B)

    # Ascent to zenith
    def dvdt(s, v, t):
        drag = get_drag(s, v)
        return -1*g - (0.5*rho(s)*drag*specs.A*v*v)/(specs.m_E + specs.m_P)

    s, v = compute_zenith(dirname, t, s, v, dsdt, dvdt, 0.1)

    return s

def search(filename, specs, min_thrust=1000, max_thrust=50000):
    min_req_thrust = (specs.m_E+specs.m_F+specs.m_P)*9.8
    specs.t_B = 5
    specs.T = min_thrust
    fp = open("usofs_search", "w")
    while specs.T <= max_thrust:
        if specs.T < min_req_thrust:
            specs.T += 500
            continue
        print "Working on thrust T=%d N..." % specs.T
        specs.t_B = 5
        zenith = 0
        while zenith < 100000:
            zenith = simulate_flight(None, specs)
            specs.t_B += 1
        fp.write("%f, %d\n" % (specs.T, specs.t_B))
        specs.T += 500
    fp.close()

def usage():

    useagestr = """Foo"""
    print usagestr

def version():

    versionstr = """USOFS Version: %s""" % str(__version__)
    print versionstr

def main():

    argstring = "a:b:e:f:ho:p:st:v"
    try:
        opts, args = gnu_getopt(argv[1:], argstring)
    except getopt.GetoptError, err:
        print str(err)
        usage()
        exit(2)
    do_search = False
    output = True
    specs = RocketSpecs(60, 1000, 30, 100, 5, pi*0.15*0.15)
    filename = "usofs_output"
    for o, a in opts:
        if o == "-a":
            specs.A = pi*a*a
        if o == "-b":
            specs.t_B = a
        if o == "-e":
            specs.m_E = a
        if o == "-f":
            specs.m_F = a
        if o == "-h":
            usage()
            exit()
        if o == "-o":
            filename = a
        if o == "-p":
            specs.m_P = a
        if o == "-s":
            do_search = True
            output = False
            filename = "usofs_search"
        if o == "-t":
            specs.T = a
        if o == "-v":
            version()
            exit()

    if do_search:
        search(filename, specs)
        exit()
    else:
        simulate_flight(filename, specs)
        exit()

if __name__ == "__main__":
    main()

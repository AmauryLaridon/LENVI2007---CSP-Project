from __future__ import print_function
from CoolProp import AbstractState
from CoolProp.CoolProp import PhaseSI, PropsSI, get_global_param_string, Props
import CoolProp.CoolProp as CoolProp
from CoolProp.HumidAirProp import HAPropsSI
from math import sin
import numpy as np

# On fait un programme pour calculer les températures du Therminol à chauffer dans le CSP
def cp(T,P, name):
    if name == "P1":
        return PropsSI('C','T',T,'P',P,'INCOMP::TVP1')*10**(-3)
    else :
        return PropsSI("d(H)/d(T)|P", "P", P, "T", T, "Water")*10**(-3)

def h (cp,T):
    return cp*T

def Power (P,m):
    return P*m

#%% DONNES

Qdotdot_1 = 270 #[kWh_th/t_s]
Qdotdot_2 = 220 #[kWh_th/t_s]
Wdotdot = 90  #[kWh_e/t_s]
T4 = 133+273.15 #[K]
T3 = 90+273.15  #[K]
T2 = 65+273.15  #[K]
T1 = T2
p2 = 3*10**5
p_atm = 101325
masse_tot = 14*10**3/6.5 #[t_s/jour]
y = np.linspace(1,24,3600) #[heures]
cp_e_T4 = cp(T4,p2,"water") #[kJ/(kg*K)]
cp_e_T3 = cp(T3,p2,"water") #[kJ/(kg*K)]
cp_e_T2 = cp(T2,p2,"water") #[kJ/(kg*K)]
cp_e_T1 = cp(T2,p2,"water") #[kJ/(kg*K)]

Tx3 = 370+273.15 #[K]
p_TVP1 = 732019.008301  #[Pa]
cp_t_Tx3 = cp(Tx3,p_TVP1,"P1")

density_salt = 1872.488 #[kg/m3]
delta_T_salt = 365-250
cp_salt = 1.53

V_tank = 0
mdot_salt = 0
flow_VP1 = 0

p5 = p_TVP1
h4 = h(cp_e_T4,T4)
h3 = h(cp_e_T3,T3)
h2 = h(cp_e_T2,T2)
h1 = h(cp_e_T1,T1)
h3_th = h(cp_t_Tx3,Tx3)


#%% Calcul du débit de sirop
masse_jour = masse_tot/24  #[t_s/h]
masse_nuit = 30/100 * masse_jour #[t_s/h]

def Debit (masse):
    Tx1=349+273.15
    Tx2 = Tx3-50
    Qdot1 = Qdotdot_1*masse ; Qdot2 = Qdotdot_2*masse ; Wdot = Wdotdot*masse 
    
    mdot_vap = (Qdot1)/(h4-h3) ; mdot_eau = (Qdot2)/(h3-h2)
               
    cp_t_Tx2 = cp(Tx2,p_TVP1,"P1") ; cp_t_Tx1 = cp(Tx1,p_TVP1,"P1")
    h1_th = h(cp_t_Tx1,Tx1) ; h2_th = h(cp_t_Tx2,Tx2)
    mdot_th = (Qdot1)/(h(cp_t_Tx3,Tx3)-h(cp_t_Tx2,Tx2))
    while (Tx1 >= Tx3-100) : #and (Tx1 - Tx3-100 > 0):
        Tx2 -= 0.001
        cp_t_Tx1 = cp(Tx1,p_TVP1,"P1") ; cp_t_Tx2 = cp(Tx2,p_TVP1,"P1")
        h1_th = h(cp_t_Tx1,Tx1) ; h2_th = h(cp_t_Tx2,Tx2)
        mdot_th = (Qdot1)/(h3_th-h2_th)
        Tx1 = cp_t_Tx2*Tx2/cp_t_Tx1 - Qdot2/(cp_t_Tx1*mdot_th)
        
    T5_0 = T4 ; T5 = T4
    cp_e_T5 = cp(T5_0,p5,"water") #4.180 #[kJ/(kg*K)]
    while T5_0-T5 <= 0.001:
        T5_0 -= 0.01
        T5 = cp_e_T4*T4/cp_e_T5 - Wdot/(0.98*mdot_vap*cp_e_T5)
        cp_e_T5 = cp(T5_0,p5,"water") #[kJ/(kg*K)]
    h5 = h(cp_e_T5,T5)
        
    return (Qdot1, Qdot2, Wdot, mdot_vap, mdot_eau, mdot_th,Tx1, Tx2, T5, h1_th,h2_th, h5)

#%% Calcul de la taille des Réservoir de sel liquide

def V_tank (masse):
    h1_th = Debit(masse)[9] ; mdot_th = Debit(masse)[5]
    mdot_salt = mdot_th*(h3_th-h1_th)/(0.98*cp_salt*delta_T_salt)
    V_tank = mdot_salt * (24-y) * 3600 / density_salt

    return (V_tank, mdot_salt, mdot_th)
   
    
def Flow_therminol (mass_day,mass_night):
    (v_tank, mdot_salt,flow_VP1) = V_tank(mass_night)
    Qdot1 = Debit(mass_day)[0] ; h1_th = Debit(mass_day)[9]
    Flow_salt_day = v_tank * density_salt /(y*3600)
    Qdot_storage = Flow_salt_day * cp_salt * delta_T_salt
    flow_VP1 = Qdot_storage / (h3_th-h1_th)
    return flow_VP1

def Condensator (masse):
    mdot_vap = Debit(masse)[3] ; h5 = Debit(masse)[11]
    return mdot_vap*(h1-h5)



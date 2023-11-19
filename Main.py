from CSP_Coolprop import *
import matplotlib.pyplot as plt
import numpy as np

mdot_th = Flow_therminol(masse_jour, masse_nuit)
(Vtank,m_salt_night, mdot_th) = V_tank(masse_nuit)

(Q1_day, Q1p_day, W_day, mdot_vap_day, mdot_eau_day, mdot_th_day) = Debit(masse_jour)[0:6] ; 
Q2_day = Condensator(masse_jour)


(Q1_night, Q1p_night, W_night, mdot_vap_night, mdot_eau_night, mdot_th_night) = Debit(masse_nuit)[0:6]
Q2_night = Condensator(masse_nuit)

VP1 = Flow_therminol(masse_jour,masse_nuit)


Figure1 = plt.figure("Maximum volume of salt needed depending on day light")
plt.plot(y,Vtank)
plt.xlabel("hours of light")
plt.ylabel("$m^{3}$")

Figure2 = plt.figure("Flow rate of therminol depending on day light")
plt.plot(y,VP1+mdot_th_day,label='Day')
plt.plot(y,VP1+mdot_th_night,label='Night')
plt.xlabel("hours of light")
plt.ylabel("$\dot{m}$ [kg/s]")
plt.legend()

print(mdot_th_day, mdot_th_night)
print(mdot_eau_day, mdot_vap_day)
print(mdot_eau_night, mdot_vap_night)
print( Q1_day, Q1p_day, W_day, Q2_day)
print( Q1_night, Q1p_night, W_night, Q2_night)

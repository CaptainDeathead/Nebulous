
for i in range(1, 6):
    r2 = 33000
    vin = 3.3
    vout = 3.3*(1-0.2*(i-1))

    try:
        r1 = r2*((vin/vout)-1)
    except:
        r1 = 0

    print(f"Resistor {i}: {int(round(r1, 0))}ohms @ {round(vout, 2)}v")
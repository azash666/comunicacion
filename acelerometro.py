from machine import I2C
import time

class Acelerometro():
    i2c = None
    """
    def __init__(self):
        # 0x0A es la dirección del acelerómetro
        self.i2c = I2C(I2C.MASTER)
        self.i2c.writeto(0x68, bytes(0x6b00))
        self.i2c.writeto_mem(0x68, 0x1C, bytes(0x08))
        
    def lee(self):
        x_data = 0
        y_data = 0
        z_data = 0

        divi = 16384
        
        x_data = int.from_bytes(self.i2c.readfrom_mem(0x68,0x3b, 1), "Big")*256+int.from_bytes(self.i2c.readfrom_mem(0x68,0x3c, 1), "Big")
        y_data = int.from_bytes(self.i2c.readfrom_mem(0x68,0x3d, 1), "Big")*256+int.from_bytes(self.i2c.readfrom_mem(0x68,0x3e, 1), "Big")
        z_data = int.from_bytes(self.i2c.readfrom_mem(0x68,0x3f, 1), "Big")*256+int.from_bytes(self.i2c.readfrom_mem(0x68,0x40, 1), "Big")
        self.i2c.readfrom(0x68, 8)
        if x_data < 32768:
            x= (x_data/divi)
        else:
            x= ((x_data-65535)/divi)
        if y_data < 32768:
            y= (y_data/divi )
        else:
            y= ((y_data-65535)/divi)
        if z_data < 32768:
            z= (z_data/divi)
        else:
            z= ((z_data-65535)/divi)
        x=x*8
        y=y*8
        z=z*8
        modulo_cuadrado = int( x * x + y * y + z * z )
        return (modulo_cuadrado,x,y,z)
    """
    def __init__(self):
        self.i2c = I2C(I2C.MASTER)
        # 0x0A es la dirección del acelerómetro
        dato1 = (0x22, 3)
        dato2 = (0x20, 0)
        while(int.from_bytes(self.i2c.readfrom_mem(0x0A, dato1[0], 1), "Big") != dato1[1]):
            print(self.i2c.writeto_mem(0x0A, dato1[0], dato1[1]))

        while(int.from_bytes(self.i2c.readfrom_mem(0x0A, dato2[0], 1), "Big") != dato2[1]):
            print(self.i2c.writeto_mem(0x0A, dato2[0], dato2[1]))
        
    def lee(self):
        x_data = 0
        y_data = 0
        z_data = 0

        divi = 8
        aux = self.i2c.readfrom_mem(0x0A, 0x04, 1)
        x_data = int.from_bytes(aux, "Big")
        y_data = int.from_bytes(self.i2c.readfrom_mem(0x0A, 0x06, 1), "Big")
        z_data = int.from_bytes(self.i2c.readfrom_mem(0x0A, 0x08, 1), "Big")
        if x_data < 128:
            x= (x_data/divi)
        else:
            x= ((x_data-256)/divi)
        if y_data < 128:
            y= (y_data/divi )
        else:
            y= ((y_data-256)/divi)
        if z_data < 128:
            z= (z_data/divi)
        else:
            z= ((z_data-256)/divi)
        modulo_cuadrado = x * x + y * y + z * z
        return (modulo_cuadrado,x,y,z)
        
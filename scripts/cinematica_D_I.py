#!/usr/bin/env python
import RPi.GPIO as GPIO
import rospy
from sensor_msgs.msg import JointState
from os import system

#------------------------------------------------------------------------------
#configurando GPIO's
#------------------------------------------------------------------------------
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

servo_1_Pin = 40
servo_2_Pin = 37
servo_3_Pin = 38
servo_4_Pin = 36
servo_5_Pin = 35
servo_6_Pin = 33

GPIO.setup(servo_1_Pin,GPIO.OUT)
GPIO.setup(servo_2_Pin,GPIO.OUT)
GPIO.setup(servo_3_Pin,GPIO.OUT)
GPIO.setup(servo_4_Pin,GPIO.OUT)
GPIO.setup(servo_5_Pin,GPIO.OUT)
GPIO.setup(servo_6_Pin,GPIO.OUT)

pwm_1=GPIO.PWM(servo_1_Pin,50)
pwm_2=GPIO.PWM(servo_2_Pin,50)
pwm_3=GPIO.PWM(servo_3_Pin,50)
pwm_4=GPIO.PWM(servo_4_Pin,50)
pwm_5=GPIO.PWM(servo_5_Pin,50)
pwm_6=GPIO.PWM(servo_6_Pin,50)

pwm_1.start(0)
pwm_2.start(0)
pwm_3.start(0)
pwm_4.start(0)
pwm_5.start(0)
pwm_6.start(0)

#------------------------------------------------------------------------------
#metodos globais
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#converte angulo em radianos para graus
#------------------------------------------------------------------------------
def rad_para_grau(junta, angulo_rad):

    if junta == 2:
        angulo_rad = angulo_rad + 2.04
        return angulo_rad * 180 / 3.142
    elif junta == 3:
        print('rad_para_gray:' + str(angulo_rad))
        angulo_rad = angulo_rad + 1.57
        return angulo_rad * 180 / 3.142
    elif junta == 5:
        angulo_rad = angulo_rad - 2.36
        return angulo_rad * 180 / 3.142
    else:
        return angulo_rad * 180 / 3.142

#------------------------------------------------------------------------------
#define limites para os angulos das juntas
#------------------------------------------------------------------------------
def calcula_limites(junta, angulo):
    if junta == 1 or junta == 6:
        if angulo < 1:
            return 0
        if angulo > 180:
            return 180
    elif junta == 2:
        if angulo < 27:
            return 27
        if angulo > 180:
            return 180
    elif junta == 3:
        if angulo < 15:
            return 15
        if angulo > 180:
            return 180
    elif junta == 4:
        if angulo < 10:
            return 10
        if angulo > 180:
            return 180
    elif junta == 5:
        if angulo < 1:
            return 0
        if angulo > 170:
            return 170
#se nao angulo nao for menor ou maior que os limites, retorna o proprio
#angulo

    return angulo

#------------------------------------------------------------------------------
#modulo de cinematica direta
#------------------------------------------------------------------------------
def cinematica_direta():
    angulos = []
    angulos.append(input('Angulo_1 desejado: '))
    angulos[0] = calcula_limites(1, angulos[0])

    angulos.append(input('Angulo_2 desejado: '))
    angulos[1] = calcula_limites(2, angulos[1])

    angulos.append(input('Angulo_3 desejado: '))
    angulos[2] = calcula_limites(3, angulos[2])

    angulos.append(input('Angulo_4 desejado: '))
    angulos[3] = calcula_limites(4, angulos[3])

    angulos.append(input('Angulo_5 desejado: '))
    angulos[4] = calcula_limites(5, angulos[4])

    angulos.append(input('Angulo_6 desejado: '))
    angulos[5] = calcula_limites(6, angulos[5])

    return angulos

#------------------------------------------------------------------------------
#modulo de cinematica inversa
#------------------------------------------------------------------------------
def cinematica_inversa(pos):
    #imprime posicoes
    print(pos)

    angulos = []
    #converte angulo recebido por mensagem para graus, dentro dos limites
    #estabelicidos    
    angulo_desejado_1 = rad_para_grau(1,  pos[0])
    angulo_desejado_1 = calcula_limites(1, angulo_desejado_1)
    angulos.append(angulo_desejado_1)

    angulo_desejado_2 = rad_para_grau(2,  pos[1])
    angulo_desejado_2 = calcula_limites(2, angulo_desejado_2)

    angulo_desejado_3 = calcula_limites(3, angulo_desejado_3)
    angulos.append(angulo_desejado_3)

    angulo_desejado_4 = rad_para_grau(4,  pos[3])
    angulo_desejado_4 = calcula_limites(4, angulo_desejado_4)
    angulos.append(angulo_desejado_4)

    angulo_desejado_5 = rad_para_grau(5,  pos[4])
    angulo_desejado_5 = calcula_limites(5, angulo_desejado_5)
    angulos.append(angulo_desejado_5)

    angulo_desejado_6 = rad_para_grau(6,  pos[5])
    angulo_desejado_6 = calcula_limites(6, angulo_desejado_6)
    angulos.append(angulo_desejado_6)

    return angulos

#------------------------------------------------------------------------------
#aplicacao princial que executa os modulos de cinematica e aciona GPIO's
#------------------------------------------------------------------------------
def programa(pos):
    #variavel que recebe angulo dos modulos de cinematica(inversa ou direta)
    angulos = []
    if modo == 0:
       angulos = cinematica_direta()
    else:
       angulos = cinematica_inversa(pos)

    DC_1 = 1./18.*(angulos[0])+2
    pwm_1.ChangeDutyCycle(DC_1)

    DC_2 = 1./18.*(angulos[1])+2
    pwm_2.ChangeDutyCycle(DC_2)

    DC_3 = 1./18.*(angulos[2])+2
    pwm_3.ChangeDutyCycle(DC_3)

    DC_4 = 1./18.*(angulos[3])+2
    pwm_4.ChangeDutyCycle(DC_4)

    DC_5 = 1./18.*(angulos[4])+2
    pwm_5.ChangeDutyCycle(DC_5)

    DC_6 = 1./18.*(angulos[5])+2
    pwm_6.ChangeDutyCycle(DC_6)

    #permite abortar a aplicacao

    if modo == 0:
        flag =  input('deseja continuar? 1-sim  0-nao')
        if flag == 0:
            rospy.signal_shutdown('Quit')

#------------------------------------------------------------------------------
#metodo que recorrente que recebe publicacoes
#------------------------------------------------------------------------------
def callback(msg):
    programa(msg.position)

#------------------------------------------------------------------------------
#'main'
#------------------------------------------------------------------------------
system('clear')
modo = input('Selecione:\n0 - cinematica direta\n1 - cinematica inversa\n')
rospy.init_node('topic_subscriber')
sub = rospy.Subscriber('joint_states', JointState, callback)
rospy.spin()

#------------------------------------------------------------------------------
#desabilita GPIO's ao finalizar script
#------------------------------------------------------------------------------
pwm_1.stop()
pwm_2.stop()
pwm_3.stop()
pwm_4.stop()
pwm_5.stop()
pwm_6.stop()
GPIO.cleanup()

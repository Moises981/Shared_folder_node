#! /usr/bin/env python
import rospy
from std_msgs.msg import Int8
import subprocess
import time



class Server(object):

    def __init__(self):
        rospy.Subscriber('/Status',Int8,self.callback)
        self.pub = rospy.Publisher('/Status',Int8,queue_size=1)
        rospy.init_node('CP_FILES')
        self.state = 0
        self.SetState = 0
        #Argumento de la contrasena de ubuntu para sudo
        self.sudoPassword = '9596'
        #Comando para montar servidor en la carpeta con sudo
        # sudo mount -t cifs -o username=Playtec,password=,dir_mode=0777,file_mode=0777 //172.16.204.128/ros /home/asus/Desktop/Test'

        self.Shared_Folder_path = '//172.16.204.128/ros'
        self.Path_ubuntu = '/home/asus/Desktop/Test'
        self.IP_FOUND = False

    def callback(self , msg):
        self.state = msg.data

    def Search_ip(self):    #Buscar el Ip del servidor 
        device_list = subprocess.Popen(['timeout','1','df','-i'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        output , error = device_list.communicate()
        for line in output.split('\n'):
            if self.Shared_Folder_path in line:
                self.IP_FOUND=True
                break
            else:
                self.IP_FOUND=False
                


    def Reconnection(self):
        #Remover tareas anteriores para evitar errores en desmontar la carpeta
        self.CP_files.kill()
        #Los comandas a ejecutar deben ser separados en arrays por argumentos
        p = subprocess.Popen(['sudo','-S','timeout','3','mount','-t','cifs','-o','username=Playtec,password=,dir_mode=0777,file_mode=0777',self.Shared_Folder_path,self.Path_ubuntu], stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
        ERR = p.communicate('{}\n'.format(self.sudoPassword))[1]
            
        #Si se logro conectar al servidor
        if p.returncode == 0:
            rospy.loginfo('Connected to the server successfully')
        
        #Sino si lanza un error vacio
        elif p.returncode!=0 and ERR!='': #Verificar si hay error
            rospy.logerr('Could not connect to the server!') #Mensaje al usuario personalizado
            rospy.logerr(ERR)
            
        #Si demora mucho en dar una respuesta el servidor entonces
        else:
            rospy.logwarn('The server is disconnected!')
            rospy.logwarn('Make sure that your IP address is correct!')
            p = subprocess.Popen(['sudo','-S','timeout','1','umount','-f',self.Path_ubuntu], stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
            p.communicate('{}\n'.format(self.sudoPassword))


    def Process(self):
        self.Search_ip()        #Buscar servidor en ubuntu
        if not self.IP_FOUND:   #Si no se encuentra intentara reconetarse
            self.SetState = 4   #Errors with the connection
            self.pub.publish(self.SetState)
            self.Reconnection()
        if self.IP_FOUND:       #Si se encuentra enviara directamente los archivos
            if self.state == 5:
                self.CP_files = subprocess.Popen(['cp','-r','/home/asus/Desktop/Catkin_ws/src/shared_folders/Backup/','/home/asus/Desktop/Test/'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                rospy.loginfo('Done')

        print self.state
        self.SetState = 0 #Esperando a recibir una entrada o simplemente esta vacia la variable
        self.pub.publish(self.SetState) #Resetea el topico

if __name__=="__main__":
    Windows = Server()
    Rate = rospy.Rate(2)
    ctrl_c = False

    def shutdownhook():
        global ctrl_c
        ctrl_c = True
        rospy.loginfo('Node cancelled')

    rospy.on_shutdown(shutdownhook)

    while not ctrl_c:
        Windows.Process()
        Rate.sleep()




    



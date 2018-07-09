from threading import Thread, Event, Timer
import http.client
import subprocess
import datetime
import time

# Global variables of the control
data_size = 0
data_size_ant = 0
stopClient = False

host = "esp-8266.local"   # Server host
port = 80                 # Server port
sample_interval = 10      # Speed data collection interval, in seconds
duration = 18000          # Duration of the speed test, in seconds (18000 = 5 hours)
ping_npackages = 1000     # Number of packets to be transferred in latency test


# Write the file header
def writeFileHeader():
    with open("speed_results.csv", "a") as myfile:
        myfile.write("Timestamp, KBps\n")

# Collects speed from time to time
def collectSpeed(stopped, interval):
    while not stopped.wait(interval):
        global data_size
        global data_size_ant
        speed = (data_size-data_size_ant)/1000/interval
        data_size_ant = data_size                       
        data_size = 0

        with open("speed_results.csv", "a") as resFile:
            resFile.write(str(time.time())+", "+str(speed)+"\n")

# Stop the execution of the speed test
def stopExecution():
    global stopClient
    stopClient = True

# Write ping statistics in file
def writePingStatistic(output):
    pac = output[0].split(',')
    transmitted = pac[0].split(' ')[0]
    received = pac[1].split(' ')[1]
    loss = pac[2].split(' ')[1]

    stat = output[1].split('=')[1].replace(' ','')
    time_min = stat.split('/')[0]
    time_avg = stat.split('/')[1]
    time_max = stat.split('/')[2]
    stddev = stat.split('/')[3].replace('ms', '')

    results = "Transmissão:\n"
    results += "Pacotes transmitidos: "+transmitted+"\n"
    results += "Pacotes recebidos: "+received+"\n"
    results += "Pacotes perdidos: "+loss+"\n"
    results += "\nEstatísticas:\n"
    results += "Menor tempo: "+time_min+" ms\n"
    results += "Tempo médio: "+time_avg+" ms\n"
    results += "Maior tempo: "+time_max+" ms\n"
    results += "Desvio padrão: "+stddev+" ms\n"
    
    with open("latency_results.txt", "a") as myfile:
        myfile.write(results)

print("-------- Teste de velocidade de transferência --------\n")
print("Coletando dados ...\n")

# Writing the file header
writeFileHeader()

# Start the connection
conn = http.client.HTTPConnection(host, port)
conn.request("GET", host)
resp = conn.getresponse()



# Duration time control of the speed benchmark
timer = Timer(duration, stopExecution)
timer.start()

# Sample capture interval control
stopFlag = Event()
t = Thread(target=collectSpeed, args=(stopFlag, sample_interval,))
t.start()

# Connection loop
while not resp.closed:
    data_size += len(resp.read(1000)) # leitura em bytes do tamanho do buffer transmitido pelo servidor
    if stopClient:
        stopFlag.set()
        resp.close()
        break

print("Os dados coletados foram armazenados no arquivo \"speed_results.csv\"\n")
print("Tempo decorrido: "+str(duration)+" segundos.\n")

# Collect latency data
print("-------- Estatísticas de latência --------\n")
print("Coletando dados ...\n")

ping = subprocess.check_output(["ping", str(host), "-c", str(ping_npackages)])
ping_output = ping.decode("utf-8").split("statistics ---\n")[1].split("\n")

writePingStatistic(ping_output)

print("Os dados coletados foram armazenados no arquivo \"latency_results.txt\"\n")


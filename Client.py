from threading import Thread, Event, Timer
import http.client
import subprocess
import datetime
import time

# Global variables of the control
data_size = 0
stopClient = False

host = "esp-8266.local"   # Host server
sample_interval = 1       # Speed data collection interval, in seconds
duration = 5              # Duration of the speed test, in seconds
ping_npackages = 10       # Number of packets to be transferred in latency test


# Write the file header
def writeFileHeader():
    with open("speed_results.csv", "a") as myfile:
        myfile.write("Timestamp, KBps\n")

# Collects speed from time to time
def collectSpeed(stopped, interval):
    while not stopped.wait(interval):
        global data_size
        speed = data_size/1000/interval

        with open("speed_results.csv", "a") as resFile:
            resFile.write(str(time.time())+", "+str(speed)+"\n")
        data_size = 0

# Stop the execution of the speed test
def stopExecution():
    global stopClient
    stopClient = True

# Show ping statistics
def showPingStatistic(output):
    pac = output[0].split(',')
    transmitted = pac[0].split(' ')[0]
    received = pac[1].split(' ')[1]
    loss = pac[2].split(' ')[1]

    stat = output[1].split('=')[1].replace(' ','')
    time_min = stat.split('/')[0]
    time_avg = stat.split('/')[1]
    time_max = stat.split('/')[2]
    stddev = stat.split('/')[3].replace('ms', '')

    print("\nTransmissão:\n")
    print("Pacotes transmitidos: "+transmitted)
    print("Pacotes recebidos: "+received)
    print("Pacotes perdidos: "+loss)
    print("\nEstatísticas:\n")
    print("Menor tempo: "+time_min+" ms")
    print("Tempo médio: "+time_avg+" ms")
    print("Maior tempo: "+time_max+" ms")
    print("Desvio padrão: "+stddev+" ms")

print("-------- Teste de velocidade de transferência --------\n")
print("Coletando dados ...\n")

# Writing the file header
writeFileHeader()

# Start the connection
conn = http.client.HTTPSConnection(host)
conn.request("GET", "/")
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
    data_size += len(resp.read())
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

showPingStatistic(ping_output)


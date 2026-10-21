import socketserver
import string


bind_ip = "10.8.0.5" 
#bind_ip = "0.0.0.0" #funziona su tutte le interfacce del dispositivo

bind_port = 9001

COMMANDS = [b'PING', b'ECHO', b'SET', b'GET']
ERROR_MESSAGE = b'ERR\n'
dictionary = dict()

class TCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        #mi serve un buffer per processare i dati
        buffer = b""

        while True:

            try:
                # Receive up to 1024 bytes of data
                user_input = self.request.recv(5000)
                print('user input', user_input)

                #se non controllo mi restituisce b'' all'infinito
                if not user_input:
                    break
                
                buffer += user_input #i pacchetti possono arrivare frammentati

                #for line in lines: #per la stessa ragione di linea 30 non posso usare il for
                while b'\n' in buffer:
                    user_input, buffer = buffer.split(b'\n', 1) #prendo un comando alla volta, sono separati da '\n'
                    line = user_input.split(b' ', 1)
                    command = line[0]

                    if command not in COMMANDS:
                        #command not allowed
                        self.request.sendall(ERROR_MESSAGE)
                        continue

                    elif command == COMMANDS[0]:
                        #PONG command
                        if len(line) > 1:
                            self.request.sendall(ERROR_MESSAGE)
                            continue

                        self.request.sendall(b'PONG\n')

                    elif command == COMMANDS[1]:
                        #ECHO COMMAND
                        if len(line) < 2:
                            self.request.sendall(ERROR_MESSAGE)
                            continue

                        data = line[1]
                        #the text must be printable
                        if all(c in string.printable for c in data.decode()) == False:
                            self.request.sendall(ERROR_MESSAGE)
                            continue

                        self.request.sendall(data+b'\n')

                    elif command == COMMANDS[2]:
                        #SET command
                        if len(line) < 2:
                            self.request.sendall(ERROR_MESSAGE)
                            continue

                        data = line[1]

                        if b' ' not in data:
                            #no value inserted
                            self.request.sendall(ERROR_MESSAGE)
                            continue

                        key, value = data.split(b' ', 1)
                        print('valore settato', value)
                        print('key presa', key)
                                            
                        #key and values must be printable --> TRASFORMALA IN UNA FUNZIONE
                        if (all(c in string.printable for c in key.decode()) == False) or (all(c in string.printable for c in value.decode()) == False):
                            self.request.sendall(ERROR_MESSAGE)
                            continue

                        dictionary[key] = value
                        #print(f'valore storato con chiave {key}', dictionary[key])

                        self.request.sendall(b'OK\n')
                    else:
                        #command GET
                        if len(line) < 2:
                            self.request.sendall(ERROR_MESSAGE)
                            continue

                        data = line[1]

                        # if data is b'':
                        #     #no value inserted
                        #     self.request.sendall(ERROR_MESSAGE)
                        #     continue

                        key = data.strip()
                        #print('chiave', key)

                        #value must be a printable string
                        if all(c in string.printable for c in key.decode()) == False:
                            self.request.sendall(ERROR_MESSAGE)
                            continue

                        value = dictionary.get(key)
                        print('returned value', value)

                        if not value or value == b'':
                            self.request.sendall(b'NOT_FOUND\n')
                        else:
                            self.request.sendall(value+b'\n')
            except ConnectionResetError:
                break
            except BrokenPipeError:
                break

if __name__ == "__main__":
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    
    with socketserver.ThreadingTCPServer((bind_ip, bind_port), TCPHandler) as server:
        print(f'Listening on {bind_ip}:{bind_port}')
        server.serve_forever()
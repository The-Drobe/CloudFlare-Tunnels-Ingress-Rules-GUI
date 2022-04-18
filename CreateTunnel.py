import os
import shutil
import csv
import subprocess


class main():
    def CreateTunnel(self, TunName, applicaton, RootDomain, Tls, CloudFlaredDir):

        hostname = TunName + "." + RootDomain

        if os.path.exists("data/config.yml") is True:
            with open("data/config.yml") as file:
                StrFile = file.read()
        else:
            StrFile = ""
        
        if os.path.exists("data/ConnectorID.txt") is True:
            with open("data/ConnectorID.txt") as file:
                out = file.read()
                out = out.replace("\n", "")

        # print(StrFile)

        if "ingress" not in StrFile:
            StrFile = ""
            # the first step of creating a tunnel
            out = os.popen("cloudflared tunnel create " + TunName).read()
            # out = subprocess.Popen("cloudflared tunnel create " + TunName)

            # gets the id of the tunnel from the output
            Location = out.find("Created tunnel " + TunName + " with id ")
            # print(Location)
            out = out[Location:]
            out = out.replace("Created tunnel " + TunName + " with id ", "")
            # print(out)
            out = out.replace("\n", "")

            StrFile = "tunnel: " + out + "\n" + "credentials-file: " + out + ".json\n" + "ingress:"
            # copy file into data
            shutil.copy(CloudFlaredDir + out + ".json", "data/" + out + ".json")
            with open("data/ConnectorID.txt", "w") as file:
                file.write(out)

        if Tls is True:
            StrFile = StrFile.replace("\n - service: http_status:404", "")
            Save = "\n - hostname: " + hostname + "\n   service: " + applicaton
            StrFile = StrFile + "\n - hostname: " + hostname + "\n   service: " + applicaton
            StrFile = StrFile + "\n - service: http_status:404"
            shut = os.popen("cloudflared tunnel route dns " + out + " " + hostname).read()
        elif Tls is False:
            StrFile = StrFile.replace("\n - service: http_status:404", "")
            Save = "\n - hostname: " + hostname + "\n   service: " + applicaton + "\n   originRequest:\n       noTLSVerify: True"
            StrFile = StrFile + "\n - hostname: " + hostname + "\n   service: " + applicaton + "\n   originRequest:\n       noTLSVerify: True"
            StrFile = StrFile + "\n - service: http_status:404"
            shut = os.popen("cloudflared tunnel route dns " + out + " " + hostname).read()


        # print(StrFile)
        with open("data/config.yml", "w") as file:
            file.write(StrFile)
        with open("data/tunnels.csv", "a") as file:
            write = hostname + "," + Save + "," + applicaton
            # This is dumb but it will work for now. Make sure that it is reconverted when used to remove entrys
            write = write.replace("\n", "n/")
            write = write + "\n"
            file.write(write)   

    def CheckIfTunnelExists(self, TunName, applicaton, RootDomain,):
        hostname = TunName + "." + RootDomain
        # read csv document into 2d list
        data = []
        if os.path.exists("data/tunnels.csv") is True:
            with open("data/tunnels.csv", errors='ignore') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',')
                for row in spamreader:
                    data.append(row)

        # print(data)

        for row in data:
            # print(row)
            try:
                if row[0] == hostname:
                    # print(hostname, "is taken please choose another one")
                    return True
                elif row[0] != hostname:
                    # print(hostname, "is available creating tunnel now")
                    return False
            except IndexError:
                # print('error')
                return False

# Copyright Giles Wardrobe 2022

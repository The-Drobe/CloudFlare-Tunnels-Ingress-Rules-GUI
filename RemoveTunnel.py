import csv
import os
import shutil
import DeleteDnsEntryCloudFlare
import CloudFlaredTaskManger
RemoveDnsEntry = DeleteDnsEntryCloudFlare.main()
CloudFlaredTaskmanger = CloudFlaredTaskManger.main()

class main():
    def RemoveTunnel(self, TunToRemove, CloudFlaredDir):
        # read csv document into 2d list
        data = []
        with open("data/tunnels.csv", errors='ignore') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',')
            for row in spamreader:
                data.append(row)
        if os.path.exists(CloudFlaredDir + "config.yml") is True:
            with open(CloudFlaredDir + "config.yml") as file:
                configyml = file.read()
        else:
            return

        with open("data/ConnectorID.txt") as file:
            ConnectorID = file.read()

        ConnectorID = ConnectorID.replace("\n", "")

        # remove tun
        Rownumb = -1
        goodrowsnumb = []
        for row in data:
            Rownumb = Rownumb + 1
            if TunToRemove == row[0]:
                removematch = str(row[1])
                # yay this again
                removematch = removematch.replace("\n", "")
                removematch = removematch.replace("n/", "\n")
                configyml = configyml.replace(removematch, "")
            else:
                goodrowsnumb.append(Rownumb)

        with open("data/config.yml", "w") as file:
            file.write(configyml)

        os.remove("data/tunnels.csv")
        with open("data/tunnels.csv", "w") as file:
            output = ""
            if goodrowsnumb != []:
                for n in goodrowsnumb:
                    output = data[n][0] + "," + data[n][1] + "," + data[n][2] + "\n"
                    # print(output)
                    file.write(output)

        EmptyFile = "ingress:\n - service: http_status:404"

        if EmptyFile in configyml:
            os.remove("data/config.yml")
            # remove tunnel
            shut = os.popen("cloudflared tunnel cleanup " + ConnectorID).read()
            shut = os.popen("cloudflared tunnel delete -f " + ConnectorID).read()
            os.remove("data/" + ConnectorID + ".json")
            return "StopCloudFlared"

# Copyright Giles Wardrobe 2022
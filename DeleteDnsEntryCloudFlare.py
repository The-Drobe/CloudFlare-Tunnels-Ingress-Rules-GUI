import CloudFlare

# ha old code is useful for something

class main():
    def main(self, ExpiredTunnels, token):
        # ExpiredTunnels is list
        # [[name, zone_id, id], [name, zone_id, id]]
        # name = test.1-0.com
        ListOfSubDomains = []
        cf = CloudFlare.CloudFlare(token=token)
        zones = cf.zones.get()
        for zone in zones:
            # print(zone['id'])
            for record in cf.zones.dns_records.get(zone['id'], params={'per_page': 100}):
                templist = []
                # print(record)
                # print(record['name'] + ',' + record['type'] + ',' + record['content'] + ',' + record['id'])
                if record['type'] == "CNAME":
                    templist.append(record['name'])
                    templist.append(record['zone_id'])
                    templist.append(record['id'])
                    ListOfSubDomains.append(templist)

        # print(ListOfSubDomains)

        for tunnel in ExpiredTunnels:
            for subListOfSubDomains in ListOfSubDomains:
                if tunnel == subListOfSubDomains[0]:
                    # print(tunnel)
                    cf.zones.dns_records.delete(subListOfSubDomains[1], subListOfSubDomains[2])

# Copyright Giles Wardrobe 2022

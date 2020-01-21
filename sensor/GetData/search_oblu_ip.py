import subprocess
import os
with open(os.devnull, "wb") as limbo:
        for n in range(233, 240):
                ip="172.17.72.{0}".format(n)
                result=subprocess.Popen(["ping", "-c", "1", "-n", "-W", "2", ip],
                        stdout=limbo, stderr=limbo).wait()
                if result:
                        # print(ip, "inactive")
                        pass
                else:
                        print(ip, "active")
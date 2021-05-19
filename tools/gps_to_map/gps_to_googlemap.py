
import os
import sys
import json

tool_path = sys.path[0]

def main(gps_file):
    output_gps_file = os.path.join(os.path.dirname(gps_file),"output_gps.txt")
    with open(gps_file, 'r') as r:
        lines = r.readlines()
    with open(output_gps_file, 'w') as fw:
        for l in lines:
            if "GPS-time" in l:
                continue
            items = l.split(',')[1:3]
            a = items[1]
            items[1] = items[0].replace("\n", "")
            items[0] = a.replace("\n", "")
            items = ''.join(["unknown unknown unknown unknown unknown ", str(items[0]), ', ',
                             str(items[1]) + ", unknown\n"])
            fw.write(items)

    cmd = ''.join(["python3 ",os.path.join(tool_path,"routemefi.py")," --input_path ",
                   output_gps_file," --save_dir ", os.path.dirname(gps_file)," --query_merge"])
    print(cmd)
    os.system(cmd)

if __name__ == '__main__':
    gps_file = sys.argv[1]
    main(gps_file)
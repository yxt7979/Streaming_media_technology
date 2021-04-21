import os
import numpy as np

FILE_PATH = './cooked_data/'
OUTPUT_PATH = './mahimahi/'
BYTES_PER_PKT = 1500.0
MILLISEC_IN_SEC = 1000.0
BITS_IN_BYTE = 8.0

# 输出单位为kbps
# 4M - 20M : 4000 - 20000 kbps

def main ():
    files = os.listdir(FILE_PATH)
    for trace_file in files:
        print(trace_file)

        with open(FILE_PATH + trace_file, 'rb') as f, open(OUTPUT_PATH + trace_file, 'a') as mf:
            time_ms = []
            bytes_recv = []
            recv_time = []
            for line in f:
                parse = line.split()
                time_ms.append(float(parse[1]))
                # bytes_recv.append(float(parse[4]))
                # recv_time.append(float(parse[5]))

            # time_ms = np.array(time_ms)
            # bytes_recv = np.array(bytes_recv)
            # recv_time = np.array(recv_time)
            # throughput_all = bytes_recv * 8 / recv_time

            millisec_time = 0
            # mf.write(str(millisec_time) + '\n')
            # M = 0
            # m = 90000000
            # for i in range(len(throughput_all)):
            #     if i < 5 : continue
            #     M = max(M,throughput_all[i])
            #     m = min(m,throughput_all[i])
            # print(M)
            # print(m)
            # midd = (20000 - 4000) / (M - m)
            # print(midd)
            for i in range(len(time_ms)):
                # if i < 5: continue
                # temp = midd * (throughput_all[i] - m) + 4000
                # throughput = temp * 4
                mf.write(str(time_ms[i] * 1024 * 5) + '\n')

                # pkt_per_millisec = throughput / BYTES_PER_PKT
                #
                # millisec_count = 0
                # pkt_count = 0
                #
                # while True:
                #     millisec_count += 1
                #     millisec_time += 1
                #     to_send = (millisec_count * pkt_per_millisec) - pkt_count
                #     to_send = np.floor(to_send)
                #
                #     mf.write(str(millisec_time) + '   ' + str(to_send) +'\n')
                #
                #     pkt_count += to_send
                #
                #     if millisec_count >= recv_time[i]:
                #         break


if __name__ == '__main__':
    main()
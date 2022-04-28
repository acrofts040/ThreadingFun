"""
Andrew Crofts
March 2022

Word Histogram is an exploration of the producer-consumer model:
    a classic problem in concurrency. 
There is one producer thread that takes in a filename, and creates
    a word histogram for every word in the text file. With this,
    there are multiple consumer threads that take the values from
    the histograms and print them concurrently.

"""

from PIL import Image
import sys
import threading
from threading import Lock,Condition

# producer function, creates histograms to be printed                                                                                                                                                                                                                         
def produce(work_queue,inp,items,mutex,ready):
    a = ""
    while not(a == "done()") and (len(ready) == 0):
        mutex.acquire()
        if (len(inp) > 0):
            a = inp.pop(0)
            if not a == "done()":
                try:
                    work_queue.append((a,create_histogram(a)))
                except:
                    print("Error: Unable to Open File")
            else:
                ready.append("terminate")

        mutex.release()


# worker function, pops histograms and prints their contents                                                                                                                                                                                                                  
def work(work_queue,inp,items,mutex,ready,outfile):
    while (len(ready) == 0) or (len(work_queue) > 0):
        mutex.acquire()
        if (len(work_queue) > 0):
            a = work_queue.pop(0)
            fname,hist = a[0],a[1]
            print_hist(fname,hist,outfile)

        mutex.release()

#takes a filename and creates the word histogram                                                                                                                                                                                                                              
def create_histogram(fname):
    words = dict()
    with open(fname,'r') as f:
        for line in f:
            for word in line.split():
                lword = word.lower()
                if not(lword in words):
                    words[lword] = 1
                else:
                    words[lword] += 1

    return words

# prints histogram in the desired style                                                                                                                                                                                                                                       
def print_hist(fname,ipthist,outfile):
    for i in ipthist:
        if outfile == "":
            print(fname,":  ",i,ipthist[i])
        else:
            towrite = fname + ":  " + i + str(ipthist[i]) + "\n"
            f = open(outfile, "a")
            f.write(towrite)
            f.close()



#runs all factors together, allocates locks and queues, and                                                                                                                                                                                                                   
#           creates threads                                                                                                                                                                                                                                                   
def run(num,outfile):
    inp = ""
    work_queue, threads, inpq = [],[],[]
    mutex,items = Lock(),Lock()
    ready = []
    
    #create producer thread
    p_args = [work_queue,inpq,items, mutex,ready]
    cur = threading.Thread(target=produce,args=p_args)
    threads.append(cur)
    cur.start()

    # create consumer threads                                                                                                                                                                                                                                                 
    for p in range(num-1):
        w_args = [work_queue,inpq,items,mutex,ready,outfile]
        cur2 = threading.Thread(target=work,args=w_args)
        cur2.start()
        threads.append(cur2)

    #take input progressively, user must input done() to terminate                                                                                                                                                                                                            
    while not(inp == "done()"):
        inp = input()
        if (inp != ""):
            inpq.append(inp)


    # join threads                                                                                                                                                                                                                                                            
    for k in threads:
        k.join()


#main function: gets number of threads and runs main functionality                                                                                                                                                                                                            
def main(args):
    if len(args) == 2:
        num = int(args[1])
    elif len(args) == 3:
        num, outfile = int(args[1]) , str(args[2])
    else:
        num = 10

    #calls important run function, handles threading, etc                                                                                                                                                                                                                     
    run(num,outfile)

#call main                                                                                                                                                                                                                                                                    

# word_histogram.py [-m max_threads] [-o outfile]                                                                                                                                                                                                                             
if __name__ == '__main__':
    main(sys.argv)


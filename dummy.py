import sys
import time

def main():
    
    print("Hello from dummy!", sys.argv)
    for i in range(20):
        sys.stdout.flush()
        time.sleep(0.2)
        print ("Number " + str(i))
    
if __name__ == "__main__": main()
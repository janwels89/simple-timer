from device import SH1106

def main():
    disp = SH1106.SH1106()
    disp.Init()
    disp.clear()

    # rest of your display code here...

if __name__ == '__main__':
    main()
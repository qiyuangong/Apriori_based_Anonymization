from pylab import *

def compare(file1, file2, var = 1):
    plotdata1 = [[],[],[]]
    plotdata2 = [[],[],[]]
    outfile1 = open('output/'+ file1,'rU')
    outfile2 = open('output/'+ file2,'rU')
    for i, line in enumerate(outfile1):
        line = line.strip()
        temp = line.split(',')
        for t in temp:
            plotdata1[i].append(t)
    for i, line in enumerate(outfile2):
        line = line.strip()
        temp = line.split(',')
        for t in temp:
            plotdata2[i].append(t)
    outfile1.close()
    outfile2.close()
    
    if var == 1: 
        #iloss
        plot(plotdata1[0], plotdata1[1],  color="blue", linewidth=2.0, linestyle="-", label="iloss" + file1)
        plot(plotdata2[0], plotdata2[1],  color="red", linewidth=2.0, linestyle="-", label="iloss" + file2)
        ylabel('iloss')
    else:
        #time
        plot(plotdata1[0], plotdata1[2],  color="blue", linewidth=2.0, linestyle="-", label="time " + file1)
        plot(plotdata2[0], plotdata2[2],  color="red", linewidth=2.0, linestyle="-", label="time " + file2)
        ylabel('time')
    # legend on 
    xlabel('K')
    legend(loc='upper left')
    # grid on
    grid(True)
    show()

def showresult(filename, var = 1):
    plotdata = [[],[],[]]
    outfile = open('output/'+ filename,'rU')
    for i, line in enumerate(outfile):
        line = line.strip()
        temp = line.split(',')
        for t in temp:
            plotdata[i].append(t)
    # print plotdata
    outfile.close()
    # iloss
    if var == 1: 
        plot(plotdata[0], plotdata[1],  color="blue", linewidth=2.0, linestyle="-", label="iloss")
        ylabel('iloss')
    else:
        #time
        plot(plotdata[0], plotdata[2],  color="red", linewidth=2.0, linestyle="-", label="time")
        ylabel('time')
    xlabel('K')
    legend(loc='upper left')
    grid(True)
    show()

#matplotlab test
if __name__ == '__main__':
    '''
    # outfile = open('data/output.txt','w')
    # plotdata = [[1,1,1,1],[2,2,2,22],[3,3,3,3]]
    plotdata = [['1','1','1','1'],['2','2','2','22'],['3','3','3','3']]
    for line in plotdata:
        temp = ''
        for t in line:
            temp += '%d,' % t
        temp = temp[:-1] + '\n'
        # temp = ','.join(line)
        # outfile.write(temp)
        print temp
    # outfile.close()   
    '''
    showresult('plot2013-11-24-20.txt', 1)
    # compare('plot2013-11-.txt','plot2013-11-19-2.txt', 2)

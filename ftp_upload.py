import ftplib


def ftpupload(filename, filepath):
	ftpfile = open("ftp",'rU')
	ftp = ftpfile.read().strip().split(' ')
	print ftp
	session = ftplib.FTP(ftp[0], ftp[1], ftp[2])
	filein = open(filepath+filename,'rb')
	session.set_pasv(0)
	session.cwd("JSSEC/QYGong")
	session.storbinary("STOR " + filename, filein)
	filein.close()
	session.quit()

if __name__ == '__main__':
	ftpupload('att_analysis','data/')

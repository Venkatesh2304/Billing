import os
from PyPDF2 import PdfFileMerger
def pdfcombine(files) :
 merger = PdfFileMerger()
 try :
  merger.append('D:\\dataprint\\output\\output.pdf')
 except :
     print()
 merger.append(files)
 merger.write('D:\\dataprint\\output\\output.pdf')
 merger.close()

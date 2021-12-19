#ADD -> 6 cc
#MUL -> 11 cc
#FADD -> 21 cc
#FMUL -> 24 cc
#Logic -> 1 cc
#Shift -> 4 cc (LSL, LSR)
#STR -> 2 cc
#LDR -> 2 cc


import os
import subprocess

#Instruction Queue
InstrQueue = [] 	#Store instructions in it (write to it from sep file)

#FP Register (For Storing Value)
cols = 2
rows = 32
FPRegister = [[i for i in range(cols)] for j in range(rows)]		#Column 0: Register (R0 to R31), Col1: Busy State
for i in range(rows):
	FPRegister[i][1] = False
	FPRegister[i][0] = i

#Reservation Stations

cols = 12
rows = 4
ReservationStAdd = [[0 for i in range(cols)] for j in range(rows)]	
ReservationStAdd[0][0] = 'WTime'
ReservationStAdd[0][1] = 'Name'
ReservationStAdd[0][2] = 'Busy'
ReservationStAdd[0][3] = 'Op'
ReservationStAdd[0][4] = 'Src1'
ReservationStAdd[0][5] = 'Src2'
ReservationStAdd[0][6] = 'Dest'
ReservationStAdd[0][7] = 'Tag1'
ReservationStAdd[0][8] = 'Tag2'
ReservationStAdd[0][9] = 'STime'
ReservationStAdd[0][10] = 'ETime'
ReservationStAdd[0][11] = 'InstrNo'

ReservationStAdd[1][0] = 0
ReservationStAdd[2][0] = 0
ReservationStAdd[3][0] = 0
ReservationStAdd[1][1] = 'Add1'
ReservationStAdd[2][1] = 'Add2'
ReservationStAdd[3][1] = 'Add3'
ReservationStAdd[1][2] = False
ReservationStAdd[2][2] = False
ReservationStAdd[3][2] = False


rows = 3
ReservationStMul = [[0 for i in range(cols)] for j in range(rows)]
ReservationStMul[0][0] = 'WTime'
ReservationStMul[0][1] = 'Name'
ReservationStMul[0][2] = 'Busy'
ReservationStMul[0][3] = 'Op'
ReservationStMul[0][4] = 'Src1'
ReservationStMul[0][5] = 'Src2'
ReservationStMul[0][6] = 'Dest'
ReservationStMul[0][7] = 'Tag1'
ReservationStMul[0][8] = 'Tag2'
ReservationStMul[0][9] = 'STime'
ReservationStMul[0][10] = 'ETime'
ReservationStMul[0][11] = 'InstrNo'

ReservationStMul[1][0] = 0
ReservationStMul[2][0] = 0
ReservationStMul[1][1] = 'Mul1'
ReservationStMul[2][1] = 'Mul2'
ReservationStMul[1][2] = False
ReservationStMul[2][2] = False

rows=3
ReservationStLogicShift = [[0 for i in range(cols)] for j in range(rows)]
ReservationStLogicShift[0][0] = 'WTime'
ReservationStLogicShift[0][1] = 'Name'
ReservationStLogicShift[0][2] = 'Busy'
ReservationStLogicShift[0][3] = 'Op'
ReservationStLogicShift[0][4] = 'Src1'
ReservationStLogicShift[0][5] = 'Src2'
ReservationStLogicShift[0][6] = 'Dest'
ReservationStLogicShift[0][7] = 'Tag1'
ReservationStLogicShift[0][8] = 'Tag2'
ReservationStLogicShift[0][9] = 'STime'
ReservationStLogicShift[0][10] = 'ETime'
ReservationStLogicShift[0][11] = 'InstrNo'

ReservationStLogicShift[1][0] = 0
ReservationStLogicShift[2][0] = 0
ReservationStLogicShift[1][1] = 'LogSh1'
ReservationStLogicShift[2][1] = 'LogSh2'
ReservationStLogicShift[1][2] = False
ReservationStLogicShift[2][2] = False


cols=10
rows=4
LoadBuffer = [[0 for i in range(cols)] for j in range(rows)]
LoadBuffer[0][0] = 'WTime'
LoadBuffer[0][1] = 'Name'
LoadBuffer[0][2] = 'Busy'
LoadBuffer[0][3] = 'Src'
LoadBuffer[0][4] = 'Dest'
LoadBuffer[0][5] = 'Tag'
LoadBuffer[0][6] = 'Addr'
LoadBuffer[0][7] = 'STime'
LoadBuffer[0][8] = 'ETime'
LoadBuffer[0][9] = 'InstrNo'

LoadBuffer[1][0] = 0
LoadBuffer[2][0] = 0
LoadBuffer[3][0] = 0
LoadBuffer[1][1] = 'Load1'
LoadBuffer[2][1] = 'Load2'
LoadBuffer[3][1] = 'Load3'
LoadBuffer[1][2] = False
LoadBuffer[2][2] = False
LoadBuffer[3][2] = False

StoreBuffer = [[0 for i in range(cols)] for j in range(rows)]
StoreBuffer[0][0] = 'WTime'
StoreBuffer[0][1] = 'Name'
StoreBuffer[0][2] = 'Busy'
StoreBuffer[0][3] = 'Src'
StoreBuffer[0][4] = 'Dest'
StoreBuffer[0][5] = 'Tag'
StoreBuffer[0][6] = 'Addr'
StoreBuffer[0][7] = 'STime'
StoreBuffer[0][8] = 'ETime'
StoreBuffer[0][9] = 'InstrNo'

StoreBuffer[1][0] = 0
StoreBuffer[2][0] = 0
StoreBuffer[3][0] = 0
StoreBuffer[1][1] = 'Store1'
StoreBuffer[2][1] = 'Store2'
StoreBuffer[3][1] = 'Store3'
StoreBuffer[1][2] = False
StoreBuffer[2][2] = False
StoreBuffer[3][2] = False


#Register status:

cols=2
rows=32
RegisterStatus = [[0 for i in range(cols)] for j in range(rows)]

for i in range(rows):
	RegisterStatus[i][0] = 'R'+str(i)

#Instruction Status
cols = 5
rows = 1
InstrStatus = [[0 for i in range(cols)] for j in range(rows)]			#further instr will be appended
InstrStatus[0][0] = 'Instr'
InstrStatus[0][1] = 'Issue'
InstrStatus[0][2] = 'Start'
InstrStatus[0][3] = 'Exec'
InstrStatus[0][4] = 'Write'

def filechange(fileo,ai,bi,ci):
    fin = open(fileo, "rt")

    fout = open("out_tb.v", "wt")

    for line in fin:
        if(line.find("33023")!=-1):
            fout.write(line.replace('33023',str(bi) ) )
        elif(line.find("36865")!=-1):
            fout.write(line.replace('36865',str(ai) ) )
        else:
            if(ci==-1):
            	fout.write(line)
            else:
            	fout.write(line.replace('8797',str(ci) ) )
        
    fin.close()
    fout.close()

def veriloginvoke(filedir,tp,ai,bi):
	os.chdir(filedir)
	fileo=filedir+"_tb.v"
	ci=-1
	if(filedir=="alu"):
		ci=tp[2]
	filechange(fileo,ai,bi,ci)
	subprocess.run(["iverilog","out_tb.v"], stdout= subprocess.PIPE,stderr= subprocess.PIPE)
	result=subprocess.run(["./a.out"],stdout= subprocess.PIPE,stderr= subprocess.PIPE)
	#print("@",result.stdout)
	os.chdir("..")
	output=[]
	for i in range(len(result.stdout)):
    		if(chr(result.stdout[i])==tp[0] and chr(result.stdout[i+1])==tp[1] ):#and chr(result.stdout[i+2])=='S' and chr(result.stdout[i+3])=='='):
        		index=i+4
        		while(chr(result.stdout[index])!='x'):
            			output.append(chr(result.stdout[index]))
            			index+=1
        		break
        
	output=int("".join(output))
	return output

#Exection Modules
def addition_integer(sno,start_time):		#integer addition#
	
	op1=FPRegister[int(ReservationStAdd[sno][4].split('R')[1])][0]
	op2=FPRegister[int(ReservationStAdd[sno][5].split('R')[1])][0]
	#print("int @",op1," %",op2)
	if (ReservationStAdd[sno][3]=='ADD'):
		opn=op2
	else:
		opn=-1*op2
	op3=veriloginvoke("rda",['1','4'],op1,opn)
	end_time = start_time + 14
	#print("int output ",op3)
	return op3, end_time

def addition_fp(sno,start_time):	#floating point addition#

	op1=FPRegister[int(ReservationStAdd[sno][4].split('R')[1])][0]
	op2=FPRegister[int(ReservationStAdd[sno][5].split('R')[1])][0]
	#print("@",op1," %",op2)
	op3=veriloginvoke("fpa",['1','2'],op1,op2)

	end_time = start_time + 20
	
	return op3, end_time

def mult_integer(sno,start_time):	#  multiplication#

	op1=FPRegister[int(ReservationStMul[sno][4].split('R')[1])][0]
	op2=FPRegister[int(ReservationStMul[sno][5].split('R')[1])][0]
	#op3=op1*op2
	flag=0
	if(op1<0):
		op1=-1*op1
		flag=1
	if(op2<0):
		op2=-1*op2
		if(flag==1):
			flag=0
		else:
			flag=1
			
	
	op3=veriloginvoke("wallace",['3','4'],op1,op2)
	if(flag==1):
		op3=-1*op3
	end_time = start_time + 34	
 
	return op3, end_time

def mult_floating(sno,start_time):	#floating point multiplication#

	op1=FPRegister[int(ReservationStMul[sno][4].split('R')[1])][0]
	op2=FPRegister[int(ReservationStMul[sno][5].split('R')[1])][0]
	#op3=op1*op2

	op3=veriloginvoke("fpm",['3','6'],op1,op2)

	print("floatmul",op1,op2,op3)
	end_time = start_time + 39

	return op3, end_time

def LogicUnit(sno,start_time):	#Logic operations
	if(ReservationStLogicShift[sno][3] == 'CMP'):
		op1=FPRegister[int(ReservationStLogicShift[sno][4].split('R')[1])][0]
		op3 = ~op1
		end_time = start_time + 0

	else:
		op1=FPRegister[int(ReservationStLogicShift[sno][4].split('R')[1])][0]
		op2=FPRegister[int(ReservationStLogicShift[sno][5].split('R')[1])][0]
		opcode="-1"
		if(ReservationStLogicShift[sno][3] == 'AND'):
			opcode="0"
		elif(ReservationStLogicShift[sno][3] == 'XOR'):
			opcode="1"
		elif(ReservationStLogicShift[sno][3] == 'NAND'):
			opcode="2"
		elif(ReservationStLogicShift[sno][3] == 'OR'):
			opcode="3"
		elif(ReservationStLogicShift[sno][3] == 'NOR'):
			opcode="5"
		elif(ReservationStLogicShift[sno][3] == 'XNOR'):
			opcode="7"
		
		if(opcode!="-1"):
			op3=veriloginvoke("alu",['1','4',str(opcode)],op1,op2)

		end_time = start_time + 0
		if(opcode=="1"):
			print("NANDresult",op1,op2,op3)

	return op3, end_time

def LogicalShift(sno,start_time):	#Shift Operations
	op1=FPRegister[int(ReservationStLogicShift[sno][4].split('R')[1])][0]
	op2=FPRegister[int(ReservationStLogicShift[sno][5].split('R')[1])][0]
	if(ReservationStLogicShift[sno][3] == 'LSR'):
		op3 = op1 >> op2
	elif(ReservationStLogicShift[sno][3] == 'LSL'):
		op3 = op1 << op2

	end_time = start_time + 3
	
	return op3, end_time


def RegisterRename(instr_no, reg_name):

	renamed_reg = 'R0'
	for i in range(31,-1,-1):
		if FPRegister[i][1] == False:
			FPRegister[i][1] = True
			renamed_reg = 'R'+str(i)
			break

	for i in range(instr_no-1, len(InstrQueue)):
		
		InstrQueue[i] = InstrQueue[i].replace(reg_name,renamed_reg)
		InstrStatus[i+1][0] = InstrStatus[i+1][0].replace(reg_name,renamed_reg)


	return renamed_reg

# Reads instruction file line by line, parses instruction, fills-in instruction queue
def ClockZeroQueue():
	choice = input('Which Instruction Set? (1 or 2)')
	if choice == 1:
		instrfile = open('Instruction1.txt','r')
	else:
		instrfile = open('Instruction2.txt','r')

	front = 0
	while(1):
		line = instrfile.readline()
		if not line:
			break

		InstrQueue.append(line.strip())

		InstrTemp = InstrQueue[front].split()
		front = front + 1
		
		if InstrTemp[0] == 'ADD' or InstrTemp[0] == 'FADD' or InstrTemp[0] == 'MUL' or InstrTemp[0] == 'NOR' or InstrTemp[0] == 'AND' or InstrTemp[0] == 'OR' or InstrTemp[0] == 'XNOR' or InstrTemp[0] == 'FMUL' or InstrTemp[0] == 'XOR' or InstrTemp[0] == 'NAND' or InstrTemp[0] == 'LSL' or InstrTemp[0] == 'LSR':
			FPRegister[int(InstrTemp[1].split('R')[1])][1] = True
			FPRegister[int(InstrTemp[2].split('R')[1])][1] = True
			FPRegister[int(InstrTemp[3].split('R')[1])][1] = True

		if InstrTemp[0] == 'LDR' or InstrTemp[0] == 'STR':
			FPRegister[int(InstrTemp[1].split('R')[1])][1] = True
			SourceAdd = InstrTemp[2].split('+')
			if len(SourceAdd) == 1:
				FPRegister[int(SourceAdd[0].split('R')[1])][1] = True
			else:
				if(SourceAdd[1][0] == 'R'):
					FPRegister[int(SourceAdd[1].split('R')[1])][1] = True
				else:
					FPRegister[int(SourceAdd[0].split('R')[1])][1] = True

		if InstrTemp[0] == 'CMP':
			FPRegister[int(InstrTemp[1].split('R')[1])][1] = True
			FPRegister[int(InstrTemp[2].split('R')[1])][1] = True
		
	for i in range(len(InstrQueue)):
		InstrStatus.append([InstrQueue[i],0,0,0,0])


	print('\nFPRegister')
	print(FPRegister)
	print('\nInstrQueue')
	for i in range(len(InstrQueue)):
		print(InstrQueue[i])
	print('\nInstrStatus')
	for i in range(len(InstrQueue)):
		print(InstrStatus[i])
	print('\n\n--------------------------------------------------------')


def CheckWAW(index, station):
	if station == 'Load':
		if RegisterStatus[int(LoadBuffer[index][4].split('R')[1])][1] != 0:
			if LoadBuffer[index][4] != LoadBuffer[index][3]:
				print('\nDATA HAZARD!!!!!!!!!!!!!!!!!!!! Renaming---------------\n')
				newname = RegisterRename(LoadBuffer[index][9],LoadBuffer[index][4])
				LoadBuffer[index][4] = newname

	elif station == 'Store':
		if RegisterStatus[int(StoreBuffer[index][4].split('R')[1])][1] != 0:
			if StoreBuffer[index][4] != StoreBuffer[index][3]:
				print('\nDATA HAZARD!!!!!!!!!!!!!!!!!!!! Renaming---------------\n')
				newname = RegisterRename(StoreBuffer[index][9],StoreBuffer[index][4])
				StoreBuffer[index][4] = newname

	elif station == 'Add':
		if RegisterStatus[int(ReservationStAdd[index][6].split('R')[1])][1] != 0:
			if ReservationStAdd[index][6] != ReservationStAdd[index][4] or ReservationStAdd[index][6] != ReservationStAdd[index][5]:
				print('\nDATA HAZARD!!!!!!!!!!!!!!!!!!!! Renaming---------------\n')
				newname = RegisterRename(ReservationStAdd[index][11],ReservationStAdd[index][6])
				ReservationStAdd[index][6] = newname

	elif station == 'Mul':
		if RegisterStatus[int(ReservationStMul[index][6].split('R')[1])][1] != 0:
			if ReservationStMul[index][6] != ReservationStMul[index][4] or ReservationStMul[index][6] != ReservationStMul[index][5]:
				print('\nDATA HAZARD!!!!!!!!!!!!!!!!!!!! Renaming---------------\n')
				newname = RegisterRename(ReservationStMul[index][11],ReservationStMul[index][6])
				ReservationStMul[index][6] = newname

	elif station == 'Log':
		if RegisterStatus[int(ReservationStLogicShift[index][6].split('R')[1])][1] != 0:
			if ReservationStLogicShift[index][6] != ReservationStLogicShift[index][4] or ReservationStLogicShift[index][6] != ReservationStLogicShift[index][5]:
				print('\nDATA HAZARD!!!!!!!!!!!!!!!!!!!! Renaming---------------\n')
				newname = RegisterRename(ReservationStLogicShift[index][11],ReservationStLogicShift[index][6])
				ReservationStLogicShift[index][6] = newname


def StartExec(clock):
	for i in range(1,4):
		if LoadBuffer[i][7] == 0 and LoadBuffer[i][2] == True:		#Busy but hasn't started (means ready to start after issue)
			if LoadBuffer[i][5] == 0: 		#No Tag, then it has to be executed else has to wait further
				LoadBuffer[i][7] = clock 	#Start time now
				InstrStatus[LoadBuffer[i][9]][2] = clock #update the start time of instruction in instruction status table
				LoadBuffer[i][8] = clock + 1

		if StoreBuffer[i][7] == 0 and StoreBuffer[i][2] == True:		#Busy but hasn't started (means ready to start after issue)
			if StoreBuffer[i][5] == 0: 		#No Tag, then it has to be executed else has to wait further
				StoreBuffer[i][7] = clock 	#Start time now
				InstrStatus[StoreBuffer[i][9]][2] = clock
				StoreBuffer[i][8] = clock + 1

		if ReservationStAdd[i][9] == 0 and ReservationStAdd[i][2] == True:
			if ReservationStAdd[i][7] == 0 and ReservationStAdd[i][8] == 0:
				ReservationStAdd[i][9] = clock
				InstrStatus[ReservationStAdd[i][11]][2] = clock
				if ReservationStAdd[i][3] == 'ADD' or ReservationStAdd[i][3] == 'SUB':
					Result, ReservationStAdd[i][10] = addition_integer(i, clock)
				elif ReservationStAdd[i][3] == 'FADD' or ReservationStAdd[i][3] == 'FSUB':
					Result, ReservationStAdd[i][10] = addition_fp(i, clock)

				FPRegister[int(ReservationStAdd[i][6].split('R')[1])][0] = Result

		if i!=3: # as there are only 2 multiplication and shift units each
			if ReservationStMul[i][9] == 0 and ReservationStMul[i][2] == True:
				if ReservationStMul[i][7] == 0 and ReservationStMul[i][8] == 0:
					ReservationStMul[i][9] = clock
					InstrStatus[ReservationStMul[i][11]][2] = clock
					if ReservationStMul[i][3] == 'MUL':
						Result, ReservationStMul[i][10] = mult_integer(i, clock)
					elif ReservationStMul[i][3] == 'FMUL':
						Result, ReservationStMul[i][10] = mult_floating(i, clock)

					FPRegister[int(ReservationStMul[i][6].split('R')[1])][0] = Result

			if ReservationStLogicShift[i][9] == 0 and ReservationStLogicShift[i][2] == True:
				if ReservationStLogicShift[i][7] == 0 and ReservationStLogicShift[i][8] == 0:
					ReservationStLogicShift[i][9] = clock
					InstrStatus[ReservationStLogicShift[i][11]][2] = clock
					if ReservationStLogicShift[i][3] == 'XOR' or ReservationStLogicShift[i][3] == 'NAND' or ReservationStLogicShift[i][3] == 'CMP' or ReservationStLogicShift[i][3] == 'AND' or ReservationStLogicShift[i][3] == 'OR' or ReservationStLogicShift[i][3] == 'NOR' or ReservationStLogicShift[i][3] == 'XNOR':
						Result, ReservationStLogicShift[i][10] = LogicUnit(i, clock)
					elif ReservationStLogicShift[i][3] == 'LSR' or ReservationStLogicShift[i][3] == 'LSL':
						Result, ReservationStLogicShift[i][10] = LogicalShift(i, clock)

					FPRegister[int(ReservationStLogicShift[i][6].split('R')[1])][0] = Result


def CompleteExec(clock):
	for i in range(1,4):
		if LoadBuffer[i][8] == clock: #if execution has ended just now
			InstrStatus[LoadBuffer[i][9]][3] = clock #update execution time in instruction status
			LoadBuffer[i][0] = clock + 1 # update write time

		if StoreBuffer[i][8] == clock:
			InstrStatus[StoreBuffer[i][9]][3] = clock
			StoreBuffer[i][0] = clock + 1

		if ReservationStAdd[i][10] == clock:
			InstrStatus[ReservationStAdd[i][11]][3] = clock
			ReservationStAdd[i][0] = clock + 1

		if i!= 3:
			if ReservationStMul[i][10] == clock:
				InstrStatus[ReservationStMul[i][11]][3] = clock
				ReservationStMul[i][0] = clock + 1

			if ReservationStLogicShift[i][10] == clock:
				InstrStatus[ReservationStLogicShift[i][11]][3] = clock
				ReservationStLogicShift[i][0] = clock + 1

def Write(clock):
	cdb = False			#Checks whether cdb is free otherwise there would be collision of data at hardware
	for i in range(1,4):
		if LoadBuffer[i][0] == clock: #if write time of the alu unit is current time
			if cdb == False: #if data bus is free
				cdb = True  #make bus busy, free up the execution unit
				LoadBuffer[i][0] = 0
				LoadBuffer[i][2] = False
				LoadBuffer[i][3] = 0

				RS_Name = RegisterStatus[int(LoadBuffer[i][4].split('R')[1])][1] #take the name of the unit
				RegisterStatus[int(LoadBuffer[i][4].split('R')[1])][1] = 0 #make the register free
				LoadBuffer[i][4] = 0

				LoadBuffer[i][5] = 0
				LoadBuffer[i][6] = 0
				LoadBuffer[i][7] = 0
				LoadBuffer[i][8] = 0
				
				InstrStatus[LoadBuffer[i][9]][4] = clock 		#Sets Instr Status to write
				LoadBuffer[i][9] = 0

				for j in range(1,4): # whichever unit has this particular exec unit as tag make those tags 0 as this unit is free now
					if LoadBuffer[j][5] == RS_Name:
						LoadBuffer[j][5] = 0
					if StoreBuffer[j][5] == RS_Name:
						StoreBuffer[j][5] = 0
					if ReservationStAdd[j][7] == RS_Name:
						ReservationStAdd[j][7] = 0
					if ReservationStAdd[j][8] == RS_Name:
						ReservationStAdd[j][8] = 0
				for j in range(1,3):
					if ReservationStMul[j][7] == RS_Name:
						ReservationStMul[j][7] = 0
					if ReservationStMul[j][8] == RS_Name:
						ReservationStMul[j][8] = 0
					if ReservationStLogicShift[j][7] == RS_Name:
						ReservationStLogicShift[j][7] = 0
					if ReservationStLogicShift[j][8] == RS_Name:
						ReservationStLogicShift[j][8] = 0

			else:
				LoadBuffer[i][0] = LoadBuffer[i][0] + 1

		if StoreBuffer[i][0] == clock:
			if cdb == False:
				cdb = True
				StoreBuffer[i][0] = 0
				StoreBuffer[i][2] = False
				StoreBuffer[i][3] = 0

				RS_Name = RegisterStatus[int(StoreBuffer[i][4].split('R')[1])][1]
				RegisterStatus[int(StoreBuffer[i][4].split('R')[1])][1] = 0
				StoreBuffer[i][4] = 0

				StoreBuffer[i][5] = 0
				StoreBuffer[i][6] = 0
				StoreBuffer[i][7] = 0
				StoreBuffer[i][8] = 0
				
				InstrStatus[StoreBuffer[i][9]][4] = clock
				StoreBuffer[i][9] = 0

				for j in range(1,4):
					if LoadBuffer[j][5] == RS_Name:
						LoadBuffer[j][5] = 0
					if StoreBuffer[j][5] == RS_Name:
						StoreBuffer[j][5] = 0
					if ReservationStAdd[j][7] == RS_Name:
						ReservationStAdd[j][7] = 0
					if ReservationStAdd[j][8] == RS_Name:
						ReservationStAdd[j][8] = 0
				for j in range(1,3):
					if ReservationStMul[j][7] == RS_Name:
						ReservationStMul[j][7] = 0
					if ReservationStMul[j][8] == RS_Name:
						ReservationStMul[j][8] = 0
					if ReservationStLogicShift[j][7] == RS_Name:
						ReservationStLogicShift[j][7] = 0
					if ReservationStLogicShift[j][8] == RS_Name:
						ReservationStLogicShift[j][8] = 0

			else:
				StoreBuffer[i][0] = StoreBuffer[i][0] + 1

		if ReservationStAdd[i][0] == clock:
			if cdb == False:
				cdb = True
				ReservationStAdd[i][0] = 0
				ReservationStAdd[i][2] = False
				ReservationStAdd[i][3] = 0
				ReservationStAdd[i][4] = 0
				ReservationStAdd[i][5] = 0

				RS_Name = RegisterStatus[int(ReservationStAdd[i][6].split('R')[1])][1]
				RegisterStatus[int(ReservationStAdd[i][6].split('R')[1])][1] = 0
				ReservationStAdd[i][6] = 0

				ReservationStAdd[i][7] = 0
				ReservationStAdd[i][8] = 0
				ReservationStAdd[i][9] = 0
				ReservationStAdd[i][10] = 0

				InstrStatus[ReservationStAdd[i][11]][4] = clock
				ReservationStAdd[i][11] = 0

				for j in range(1,4):
					if LoadBuffer[j][5] == RS_Name:
						LoadBuffer[j][5] = 0
					if StoreBuffer[j][5] == RS_Name:
						StoreBuffer[j][5] = 0
					if ReservationStAdd[j][7] == RS_Name:
						ReservationStAdd[j][7] = 0
					if ReservationStAdd[j][8] == RS_Name:
						ReservationStAdd[j][8] = 0
				for j in range(1,3):
					if ReservationStMul[j][7] == RS_Name:
						ReservationStMul[j][7] = 0
					if ReservationStMul[j][8] == RS_Name:
						ReservationStMul[j][8] = 0
					if ReservationStLogicShift[j][7] == RS_Name:
						ReservationStLogicShift[j][7] = 0
					if ReservationStLogicShift[j][8] == RS_Name:
						ReservationStLogicShift[j][8] = 0

			else:
				ReservationStAdd[i][0] = ReservationStAdd[i][0] + 1

		if i!=3:
			if ReservationStMul[i][0] == clock:
				if cdb == False:
					cdb = True
					ReservationStMul[i][0] = 0
					ReservationStMul[i][2] = False
					ReservationStMul[i][3] = 0
					ReservationStMul[i][4] = 0
					ReservationStMul[i][5] = 0

					RS_Name = RegisterStatus[int(ReservationStMul[i][6].split('R')[1])][1]
					RegisterStatus[int(ReservationStMul[i][6].split('R')[1])][1] = 0
					ReservationStMul[i][6] = 0

					ReservationStMul[i][7] = 0
					ReservationStMul[i][8] = 0
					ReservationStMul[i][9] = 0
					ReservationStMul[i][10] = 0

					InstrStatus[ReservationStMul[i][11]][4] = clock
					ReservationStMul[i][11] = 0

					for j in range(1,4):
						if LoadBuffer[j][5] == RS_Name:
							LoadBuffer[j][5] = 0
						if StoreBuffer[j][5] == RS_Name:
							StoreBuffer[j][5] = 0
						if ReservationStAdd[j][7] == RS_Name:
							ReservationStAdd[j][7] = 0
						if ReservationStAdd[j][8] == RS_Name:
							ReservationStAdd[j][8] = 0
					for j in range(1,3):
						if ReservationStMul[j][7] == RS_Name:
							ReservationStMul[j][7] = 0
						if ReservationStMul[j][8] == RS_Name:
							ReservationStMul[j][8] = 0
						if ReservationStLogicShift[j][7] == RS_Name:
							ReservationStLogicShift[j][7] = 0
						if ReservationStLogicShift[j][8] == RS_Name:
							ReservationStLogicShift[j][8] = 0
				else:
					ReservationStMul[i][0] = ReservationStMul[i][0] + 1

			if ReservationStLogicShift[i][0] == clock:
				if cdb == False:
					cdb = True
					ReservationStLogicShift[i][0] = 0
					ReservationStLogicShift[i][2] = False
					ReservationStLogicShift[i][3] = 0
					ReservationStLogicShift[i][4] = 0
					ReservationStLogicShift[i][5] = 0

					RS_Name = RegisterStatus[int(ReservationStLogicShift[i][6].split('R')[1])][1]
					RegisterStatus[int(ReservationStLogicShift[i][6].split('R')[1])][1] = 0
					ReservationStLogicShift[i][6] = 0

					ReservationStLogicShift[i][7] = 0
					ReservationStLogicShift[i][8] = 0
					ReservationStLogicShift[i][9] = 0
					ReservationStLogicShift[i][10] = 0

					InstrStatus[ReservationStLogicShift[i][11]][4] = clock
					ReservationStLogicShift[i][11] = 0

					for j in range(1,4):
						if LoadBuffer[j][5] == RS_Name:
							LoadBuffer[j][5] = 0
						if StoreBuffer[j][5] == RS_Name:
							StoreBuffer[j][5] = 0
						if ReservationStAdd[j][7] == RS_Name:
							ReservationStAdd[j][7] = 0
						if ReservationStAdd[j][8] == RS_Name:
							ReservationStAdd[j][8] = 0
					for j in range(1,3):
						if ReservationStMul[j][7] == RS_Name:
							ReservationStMul[j][7] = 0
						if ReservationStMul[j][8] == RS_Name:
							ReservationStMul[j][8] = 0
						if ReservationStLogicShift[j][7] == RS_Name:
							ReservationStLogicShift[j][7] = 0
						if ReservationStLogicShift[j][8] == RS_Name:
							ReservationStLogicShift[j][8] = 0

				else:
					ReservationStLogicShift[i][0] = ReservationStLogicShift[i][0] + 1

def printfp():
	for i in range(len(FPRegister)):
		print("R",i," ",FPRegister[i][0]," ")

def MainFunction():

	clock = 0
	ClockZeroQueue()
	front = 0
	rear = len(InstrQueue) - 1

	while(1):			
		counter = 0 # to count number of completed instructions
		clock = clock + 1

		print('clock = ' + str(clock))

		for i in range(len(InstrQueue)):
			if InstrStatus[i][4] != 0: # if write operation of instruction is completed, increment counter
				counter = counter + 1

		if counter == len(InstrQueue):		#Tomasulo keeps running until all instr has completed write back
			break

		StartExec(clock)

		if(front <= rear):
			tempInstr = InstrQueue[front].split() # instruction to be executed
			# print(tempInstr)
	
			if tempInstr[0] == 'LDR':
				for i in range(1,4):
					if(LoadBuffer[i][2] == False):  # check from freeness of execution unit

						InstrStatus[front+1][1] = clock 	#update Issue time in instruction status table

						LoadBuffer[i][2] = True		#make the exec unit busy
						SourceAdd = tempInstr[2].split('+')
						#setting load buffer columns
						if len(SourceAdd) == 1:
							LoadBuffer[i][3] = SourceAdd[0]
						else:
							if(SourceAdd[1][0] == 'R'):
								LoadBuffer[i][3] = SourceAdd[1]
								LoadBuffer[i][6] = SourceAdd[0]
							else:
								LoadBuffer[i][3] = SourceAdd[0]
								LoadBuffer[i][6] = SourceAdd[1]
						LoadBuffer[i][4] = tempInstr[1]
						LoadBuffer[i][5]=RegisterStatus[int(LoadBuffer[i][3].split('R')[1])][1]#source tag update 

						LoadBuffer[i][9] = front + 1

						CheckWAW(i,'Load')
						RegisterStatus[int(LoadBuffer[i][4].split('R')[1])][1] = LoadBuffer[i][1] # update the register being used with the exec unit name
						
						front = front + 1		#Dequeue the Instr Queue
						break


			elif tempInstr[0] == 'STR':
				for i in range(1,4):
					if(StoreBuffer[i][2] == False):

						InstrStatus[front+1][1] = clock 	#set Issue

						StoreBuffer[i][2] = True		#Now it is busy
						SourceAdd = tempInstr[2].split('+')
						if len(SourceAdd) == 1:
							StoreBuffer[i][4] = SourceAdd[0]
						else:
							if(SourceAdd[1][0] == 'R'):
								StoreBuffer[i][4] = SourceAdd[1]
								StoreBuffer[i][6] = SourceAdd[0]
							else:
								StoreBuffer[i][4] = SourceAdd[0]
								StoreBuffer[i][6] = SourceAdd[1]
						StoreBuffer[i][3] = tempInstr[1]
						StoreBuffer[i][5]=RegisterStatus[int(StoreBuffer[i][3].split('R')[1])][1]#source tag update

						StoreBuffer[i][9] = front + 1
						
						CheckWAW(i,'Store')
						RegisterStatus[int(StoreBuffer[i][4].split('R')[1])][1] = StoreBuffer[i][1]
						
						front = front + 1
						break


			elif tempInstr[0] == 'ADD' or tempInstr[0] == 'FADD' or tempInstr[0] == 'SUB' or tempInstr[0] == 'FSUB':
				for i in range(1,4):
					if(ReservationStAdd[i][2] == False):

						InstrStatus[front+1][1] = clock 	#set Issue

						ReservationStAdd[i][2] = True		#Now it is busy
						ReservationStAdd[i][3] = tempInstr[0]
						ReservationStAdd[i][4] = tempInstr[2]
						ReservationStAdd[i][5] = tempInstr[3]
						ReservationStAdd[i][6] = tempInstr[1]

						ReservationStAdd[i][7]=RegisterStatus[int(ReservationStAdd[i][4].split('R')[1])][1]#tag  updation of source registers
						ReservationStAdd[i][8]=RegisterStatus[int(ReservationStAdd[i][5].split('R')[1])][1]

						ReservationStAdd[i][11] = front + 1		#instrno is front + 1 (1,2,3)

						CheckWAW(i,'Add')
						RegisterStatus[int(ReservationStAdd[i][6].split('R')[1])][1] = ReservationStAdd[i][1]

						front = front + 1
						break


			elif tempInstr[0] == 'MUL' or tempInstr[0] == 'FMUL':
				for i in range(1,3):
					if(ReservationStMul[i][2] == False):

						InstrStatus[front+1][1] = clock 	#set Issue

						ReservationStMul[i][2] = True		#Now it is busy
						ReservationStMul[i][3] = tempInstr[0]
						ReservationStMul[i][4] = tempInstr[2]
						ReservationStMul[i][5] = tempInstr[3]
						ReservationStMul[i][6] = tempInstr[1]
						ReservationStMul[i][7]=RegisterStatus[int(ReservationStMul[i][4].split('R')[1])][1]#tag  updation of source registers
						ReservationStMul[i][8]=RegisterStatus[int(ReservationStMul [i][5].split('R')[1])][1]

						ReservationStMul[i][11] = front + 1		#instrno is front + 1 (1,2,3)
						
						CheckWAW(i,'Mul')
						RegisterStatus[int(ReservationStMul[i][6].split('R')[1])][1] = ReservationStMul[i][1]
						
						front = front + 1
						break

			elif tempInstr[0] == 'CMP' or tempInstr[0] == 'XOR' or tempInstr[0] == 'NAND' or tempInstr[0] == 'XNOR' or tempInstr[0] == 'AND' or tempInstr[0] == 'OR' or tempInstr[0] == 'NOR' or tempInstr[0] == 'LSL' or tempInstr[1] == 'LSR':
				for i in range(1,4):
					if(ReservationStLogicShift[i][2] == False):
						
						InstrStatus[front+1][1] = clock 	#set Issue

						ReservationStLogicShift[i][2] = True		#Now it is busy
						ReservationStLogicShift[i][3] = tempInstr[0]
						ReservationStLogicShift[i][4] = tempInstr[2]
						if tempInstr[0] != 'CMP':
							ReservationStLogicShift[i][5] = tempInstr[3]
							ReservationStLogicShift[i][8]=RegisterStatus[int(ReservationStLogicShift[i][5].split('R')[1])][1]#tag
						ReservationStLogicShift[i][6] = tempInstr[1]
						ReservationStLogicShift[i][7]=RegisterStatus[int(ReservationStLogicShift[i][4].split('R')[1])][1]#tag

						ReservationStLogicShift[i][11] = front + 1		#instrno is front + 1 (1,2,3)
						
						CheckWAW(i,'Log')
						RegisterStatus[int(ReservationStLogicShift[i][6].split('R')[1])][1] = ReservationStLogicShift[i][1]
						
						front = front + 1
						break


		CompleteExec(clock)
		Write(clock)
		printfp()


		print('Instruction Status:')
		for i in range(len(InstrQueue)+1):
			print(InstrStatus[i][0],"\t",InstrStatus[i][1],"\t",InstrStatus[i][3],"\t",InstrStatus[i][4])
		print('\nLoadBuffer:')
		for i in range(4):
			print(LoadBuffer[i][1],"\t",LoadBuffer[i][2],"\t",LoadBuffer[i][3],"\t",LoadBuffer[i][5],"\t",LoadBuffer[i][6])
		print('\nStoreBuffer:')
		for i in range(4):
			print(StoreBuffer[i][1],"\t",StoreBuffer[i][2],"\t",StoreBuffer[i][3],"\t",StoreBuffer[i][5],"\t",StoreBuffer[i][6])
		print('\nReservationStAdd')
		for i in range(4):
			print(ReservationStAdd[i][1],"\t",ReservationStAdd[i][2],"\t",ReservationStAdd[i][3],"\t",ReservationStAdd[i][4],"\t",ReservationStAdd[i][5],"\t",ReservationStAdd[i][7],"\t",ReservationStAdd[i][8])
		print('\nReservationStMul')
		for i in range(3):
			print(ReservationStMul[i][1],"\t",ReservationStMul[i][2],"\t",ReservationStMul[i][3],"\t",ReservationStMul[i][4],"\t",ReservationStMul[i][5],"\t",ReservationStMul[i][7],"\t",ReservationStMul[i][8])
		print('\nReservationStLogicShift')
		for i in range(3):
			print(ReservationStLogicShift[i][1],"\t",ReservationStLogicShift[i][2],"\t",ReservationStLogicShift[i][3],"\t",ReservationStLogicShift[i][4],"\t",ReservationStLogicShift[i][5],"\t",ReservationStLogicShift[i][7],"\t",ReservationStLogicShift[i][8])
		print('\nRegisterStatus')
		
		print(RegisterStatus)

		print('\n-------------------------------------------------------------------\n')




MainFunction()

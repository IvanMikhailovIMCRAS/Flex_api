import os
import shutil
import numpy as np
import subprocess
import matplotlib.pyplot as plt
import operator

class Flex_api:
	def __init__(self, N1, sigma1, p1, chi1, N2, sigma2, p2, chi2):
		self.N1 = N1                        #polymerization degree
		self.sigma1 = sigma1                #grafting density
		self.p1 = p1                        #Kuhn length
		self.chi1 = chi1                    #Flory's parameter for polymer-solvent
		self.N2 = N2                        #polymerization degree
		self.sigma2 = sigma2                #grafting density
		self.p2 = p2                        #Kuhn length
		self.chi2 = chi2                    #Flory's parameter for polymer-solvent
		self.chi12 = 0.0                    #Flory's parameter for polymer-polymer
		self.eta = 0.04  
		self.ksi = 0.1                      #step size of gradient descent
		self.nfree = 5000                   #number of "free steps" at descent
		self.swpro = 1                      #if swpro=0: switch off print of profile
        
	def print_input(self):
		with open('INPUT.txt', 'w') as f:
			f.write(f'{self.N1} \n')
			f.write(f'{self.sigma1} \n')
			f.write(f'{self.p1} \n')
			f.write(f'{self.chi1} \n')
			f.write(f'{self.N2} \n')
			f.write(f'{self.sigma2} \n')
			f.write(f'{self.p2} \n')
			f.write(f'{self.chi2} \n')
			f.write(f'{self.chi12} \n')
			f.write(f'{self.eta} \n')
			f.write(f'{self.ksi} \n')
			f.write(f'{self.nfree} \n')
			f.write(f'{self.swpro} \n')
    
	@staticmethod
	def check_infor():
		try:
			path = str(os.system('pwd'))
			if os.name == 'nt':
				path = path+r'\INFOR.info'
			else:
				path = path+r'/INFOR.info'
			with open(path, 'r') as file:
				array = [row.strip() for row in file]
			if 'Awesome! Everything was working as it should!' in array:
				return True
		except:
			return False

	@staticmethod
	def read_data():
		try:
			with open('data.out', 'r') as data:
				data.readline()
				st = list(map(float, data.readline().split()))
				H1 = st[0]
				H2 = st[1]
			return H1, H2
		except:
			return None

	@staticmethod
	def run_flex(timeout):
		if os.name == 'nt':
			command = r'.\flex.exe'
		else:
			command = r'./flex.exe'
		try:
			proc = subprocess.run(command, timeout=timeout, check=True, stdout=subprocess.PIPE, encoding='utf-8')
			print(proc.stdout) 
		except:
			return False
		return True
	
	@staticmethod
	def load_flex():
		dir_name = 'Flex_2_2/Source'
		try:
			shutil.rmtree('Flex_2_2')
		except:
			pass
		os.system('git clone https://github.com/IvanMikhailovIMCRAS/Flex_2_2.git')
		os.chdir(dir_name) 
		os.system('make')
		os.chdir('..')
		os.chdir('..')
		shutil.copy('Flex_2_2/flex.exe','flex.exe')

	@staticmethod
	def clear():
		for file in ['data.out', 'INFOR.info','INPUT.txt']:
			try:
				os.remove(file)
			except:
				pass
						
	@staticmethod
	def clear_initial_guess():
		try:
			os.remove('initial_guess.in')
		except:
			pass

def run_on_chi(Point, chi2, timeout = 300):
	Point.chi2 = chi2
	Flex_api.clear()
	Point.print_input()
	if Point.run_flex(timeout):
		return Flex_api.read_data()
	else:
		return None

if __name__ == '__main__':
    EPS = 1e-4
    DELTA = 0.2
    Point = Flex_api(100, 0.05, 1.0, 0.0, 150, 0.05, 1.0, 0.25)
    if not os.path.isfile('flex.exe'):
        Flex_api.load_flex()
    H1, H2 = list(), list() 
    delta = DELTA
    chi = [-delta]
    while delta > EPS:
        chi[-1] += delta
        Flex_api.clear()
        Flex_api.clear_initial_guess()
        calc = run_on_chi(Point, chi[-1])
        if calc:
            t1, t2 = calc
            H1.append(t1)
            H2.append(t2)
            print(chi[-1], H1[-1], H2[-1])
            if H2[-1] <= H1[-1]:
                chi.append(chi[-1] - delta)
                delta = 0.5 * delta
            else:
                chi.append(chi[-1])
        else:
            break
    chi.pop(-1)
    
    L = sorted(zip(chi,H1,H2), key=operator.itemgetter(0))
    chi, H1, H2 = zip(*L)
    plt.plot(chi, H1, '-o', color = 'b')
    plt.plot(chi, H2, '-o', color = 'r')
    plt.show()
	

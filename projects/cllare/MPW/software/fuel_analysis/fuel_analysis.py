from math import exp

class Stack:

	def __init__(self, cm_mass, ll_mass, pm_mass, astronaut_mass, suit_mass):
		self.cm_mass = cm_mass
		self.ll_mass = ll_mass
		self.pm_mass = pm_mass
		self.astronaut_mass = astronaut_mass
		self.suit_mass = suit_mass

	def tli_mass(self):

		return self.cm_mass + self.ll_mass + self.pm_mass + self.astronaut_mass + self.suit_mass
	def loi_mass(self):

		return self.cm_mass + self.ll_mass + self.pm_mass + self.astronaut_mass + self.suit_mass

	def landing_mass(self):

		return self.ll_mass + self.astronaut_mass + self.suit_mass

	def tei_mass(self):

		return self.cm_mass + self.pm_mass + self.astronaut_mass + self.suit_mass


class DeltaVBudget:
	
	def __init__(self, tli, loi, lander, tei):
		self.tli = 1.1*tli
		self.loi = 1.1*loi
		self.lander = 1.1*lander
		self.tei = 1.1*tei

def rocket_eq(empty_mass, deltav, isp):

	return empty_mass*(exp(deltav / (9.8*isp))-1)

def compute_total_mass(stack, budget, isp):

	lander_fuel = rocket_eq(stack.landing_mass(), budget.lander, isp)
	tei_fuel = rocket_eq(stack.tei_mass(), budget.tei, isp)
	loi_fuel = rocket_eq(stack.loi_mass() + lander_fuel + tei_fuel, budget.loi, isp)
	tli_fuel = rocket_eq(stack.tli_mass() + lander_fuel + tei_fuel + loi_fuel, budget.tli, isp)
	return stack.tli_mass() + lander_fuel + tei_fuel + loi_fuel + tli_fuel

def main():

	super_heavy_stack = Stack(1750, 600, 1000, 75, 25)
	heavy_stack = Stack(1500, 500, 750, 75, 25)
	med_stack = Stack(1250, 400, 500, 75, 25)
	light_stack = Stack(1000, 300, 250, 75, 25)
	super_light_stack = Stack(750, 200, 125, 75, 25)

	budget = DeltaVBudget(3100, 1000, 3400, 700)

	fp = open("fuel_analysis.txt","w")
	fp.write("Isp, \"Super light\", Light, Medium, Heavy, \"Super heavy\"\n")
	for isp in range(250, 500, 10):
		a = compute_total_mass(super_light_stack, budget, isp)
		b = compute_total_mass(light_stack, budget, isp)
		c = compute_total_mass(med_stack, budget, isp)
		d = compute_total_mass(heavy_stack, budget, isp)
		e = compute_total_mass(super_heavy_stack, budget, isp)
		fp.write("%d, %f, %f, %f, %f, %f\n" % (isp, a, b, c, d, e))
	fp.close()

if __name__ == "__main__":

	main()

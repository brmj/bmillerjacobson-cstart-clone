from math import exp

class Stack:

	def __init__(self, cm_mass, osm_mass, ll_mass, pm_mass, astronaut_mass, suit_mass):
		self.cm_mass = cm_mass
		self.osm_mass = osm_mass
		self.ll_mass = ll_mass
		self.pm_mass = pm_mass
		self.astronaut_mass = astronaut_mass
		self.suit_mass = suit_mass


	def tli_mass(self):

		return self.cm_mass + self.osm_mass + self.ll_mass + self.pm_mass + self.astronaut_mass + self.suit_mass
	def loi_mass(self):

		return self.cm_mass + self.osm_mass + self.ll_mass + self.pm_mass + self.astronaut_mass + self.suit_mass

	def landing_mass(self):

		return self.ll_mass + self.astronaut_mass + self.suit_mass

	def tei_mass(self):

		return self.cm_mass + self.osm_mass + self.pm_mass + self.astronaut_mass + self.suit_mass


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

	cm_mass = 1114
	osm_mass = 200
	ll_mass = 400
	pm_mass = 500
	astronaut_mass = 75
	suit_mass = 25
	
	super_heavy_stack = Stack(1.2*cm_mass, 1.2*osm_mass, 1.2*ll_mass, 1.2*pm_mass, astronaut_mass, 1.2*suit_mass)
	heavy_stack = Stack(1.1*cm_mass, 1.1*osm_mass, 1.1*ll_mass, 1.1*pm_mass, astronaut_mass, 1.1*suit_mass)
	med_stack = Stack(cm_mass, osm_mass, ll_mass, pm_mass, astronaut_mass, suit_mass)
	light_stack = Stack(0.9*cm_mass, 0.9*osm_mass, 0.9*ll_mass, 0.9*pm_mass, astronaut_mass, 0.9*suit_mass)
	super_light_stack = Stack(0.8*cm_mass, 0.8*osm_mass, 0.8*ll_mass, 0.8*pm_mass, astronaut_mass, 0.8*suit_mass)

	budget = DeltaVBudget(3276, 1000, 4200, 700)

	fp = open("fuel_analysis.txt","w")
	fp.write("Isp, \"Super light\", Light, Medium, Heavy, \"Super heavy\"\n")
	for isp in range(250, 501, 10):
		a = compute_total_mass(super_light_stack, budget, isp)
		b = compute_total_mass(light_stack, budget, isp)
		c = compute_total_mass(med_stack, budget, isp)
		d = compute_total_mass(heavy_stack, budget, isp)
		e = compute_total_mass(super_heavy_stack, budget, isp)
		fp.write("%d, %f, %f, %f, %f, %f\n" % (isp, a, b, c, d, e))
	fp.close()

if __name__ == "__main__":

	main()

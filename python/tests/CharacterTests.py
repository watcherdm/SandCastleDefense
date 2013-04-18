from entities import Characters

class CharacterTests():
	def test(self):
		print dir(Characters)
		for cls in Characters:
			print cls

if __name__ == "__main__":
	CharacterTests().test()
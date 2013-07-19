import unittest
import python.engines.trajectory as trajectory
import random

class Testtrajectoryinitialization(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def testInheritance(self):
        actual = trajectory.Cannonball
        expected_parent = trajectory.Projectile
        print "Is Cannonball a subclass of Projectile:", issubclass(actual, expected_parent)
        self.assertTrue(issubclass(actual, expected_parent), "Error in Cannonball trajectory inheritance")
        self.assertFalse(issubclass(expected_parent, actual), "Error in Cannonball trajectory inheritance")
    
    def testPhysicsInheritance(self):
        P = trajectory.Physics()
        actual = trajectory.Cannonball(P)
        expected = -9.81
        self.assertAlmostEqual(actual.P.gravity, expected, 2, "Error in initial cannonball inheritance of physics")
        P.gravity = -4.32
        expected = -4.32
        self.assertAlmostEqual(actual.P.gravity, expected, 2, "Error in updating cannonball physics inheritance")


#Test equations for conservation of energy in a constant force field.    
class Testbasiccannonball(unittest.TestCase):
    
    def setUp(self):
        self.numbertests = 1000
        pass
    
    def conservativeEnergy(self, r, Force): #Equation only works for systems with constant force fields, aka: the basic cannonball
        E = 0
        for i in range(3):
            E += -Force[i]*r[0, i] + .5*(r[1,i]**2)
    
    class conservativeCannonball(trajectory.Projectile):
        def __init__(self, phys_constants):
            self.P = phys_constants
    
        def diff_eqs(self, *kwargs):
            return [[self.r[-1,1]],[0, 0, -9.81]]
        
    def createProjectile(self):
        ball = self.conservativeCannonball(trajectory.Physics)
        for i, val in enumerate(ball.r[0,0]):
            ball.r[0,i] = random.randrange(1000)
        for i, val in enumerate(ball.r[0,1]):
            ball.r[1,i] = random.randrange(100)
        return ball
    
    def testEnergy(self):
        for i in range(self.numbertests):
            B = self.createProjectile()
            B.calculate_trajectory(B.diff_eqs)
            actual = self.conservativeEnergy(B.r[-1], B.diff_eqs()[1])
            expected = self.conservativeEnergy(B.r[0], B.diff_eqs()[1])
            self.assertAlmostEqual(actual, expected, 3, "Energy conservation failure with initial conditions: \n %s \n Initial energy: %s \n Final energy %s" % (B.r[0], expected, actual))
    
    def testBoundaries(self):
        for i in range(self.numbertests):
            B = self.createProjectile()
            B.calculate_trajectory(B.diff_eqs)
            for i, val in enumerate(B.r):
                actual = val[0,2]
                self.assertGreaterEqual(val, 0, "Projectile exceeded lower Z axis bounds with initial conditions: \n $s" % (B.r[0]))
                self.assertLessEqual(val, 1000, "Projectile exceeded upper Z axis bounds with initial conditions: \n $s" % (B.r[0]))
                
            
        
    
    
        
        
    
    
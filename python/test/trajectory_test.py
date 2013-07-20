import unittest
import python.engines.trajectory as trajectory
import random
import numpy as np

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
        self.numbertests = 100
        pass
    
    def conservativeEnergy(self, r, Force): #Equation only works for systems with constant force fields, aka: the basic cannonball
        E = 0
        for i in range(3):
            E += -Force[i]*r[0, i] + .5*(r[1,i]**2)
    
    class conservativeCannonball(trajectory.Projectile):
        def __init__(self, phys_constants):
            trajectory.Projectile.__init__(self)
            self.P = phys_constants
            self.diff_eqs_args = {}
        
        def diff_eqs(self, r, t, *kwargs):
            return np.append([r[1]],[[0, 0, self.P.gravity]], axis = 0)
        
        def calculate_trajectory(self):
            self.rk4(self.diff_eqs, self.diff_eqs_args)
        
    def createProjectile(self):
        ball = self.conservativeCannonball(trajectory.Physics())
        for i, val in enumerate(ball.r_set[0,0]):
            ball.r_set[0,0,i] = random.randrange(1000)
        for i, val in enumerate(ball.r_set[0,1]):
            ball.r_set[0,1,i] = random.randrange(100)
        return ball
    
    def testEnergy(self):
        for i in range(self.numbertests):
            B = self.createProjectile()
            B.calculate_trajectory()
            actual = self.conservativeEnergy(B.r_set[-1], B.diff_eqs(B.r_set[0], B.localtime)[1])
            expected = self.conservativeEnergy(B.r_set[0], B.diff_eqs(B.r_set[-1], B.localtime)[1])
            self.assertAlmostEqual(actual, expected, 3, "Energy conservation failure with initial conditions: \n %s \n Initial energy: %s \n Final energy %s" % (B.r_set[0], expected, actual))
    
    def testBoundaries(self):
        for i in range(self.numbertests):
            B = self.createProjectile()
            B.calculate_trajectory()
            for i, val in enumerate(B.r_set):
                actual = val[0,2]
                self.assertGreaterEqual(actual, 0, "Projectile exceeded lower Z axis bounds with initial conditions: \n %s" % (B.r_set[0]))
                self.assertLessEqual(actual, 1000, "Projectile exceeded upper Z axis bounds with initial conditions: \n %s" % (B.r_set[0]))
                
            
        
    
    
        
        
    
    
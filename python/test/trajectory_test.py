import unittest
import python.engines.trajectory as trajectory
import random
import numpy as np
from math import pi, sin, cos
import pygame

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
    
    def testSettingInitialConditions(self):
        B = trajectory.Cannonball(trajectory.Physics())
        expected_v = float(60)
        expected_p = [0,0,50]
        B.set_initial_conditions([0,0,50],0, pi/4, expected_v)
        actual_v = (B.r_set[0,1,0]**2 + B.r_set[0,1,1]**2 + B.r_set[0,1,2]**2)**(.5)
        actual_p = B.r_set[0,0]
        print "velocity check: (actual, expected)", actual_v, expected_v
        print "position check: (actual, expected)", actual_p, expected_p
        for i in range(2):
            self.assertAlmostEqual(expected_p[i], actual_p[i], 0, "error in setting projectile initial position along coordinate %s" % i)
        self.assertLess(abs(expected_v - actual_v), 1, "error in setting projectile initial velocity")
        

#Test equations for conservation of energy in a constant force field.    
class Testbasiccannonball(unittest.TestCase):
    
    def setUp(self):
        self.numbertests = 10
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
                print i, val
                actual = val[0,2]
                self.assertGreaterEqual(actual, 0, "Projectile exceeded lower Z axis bounds with initial conditions: \n %s" % (B.r_set[0]))
                self.assertLessEqual(actual, 1000, "Projectile exceeded upper Z axis bounds with initial conditions: \n %s" % (B.r_set[0]))
                
class testCannonImplementation(unittest.TestCase):
    
    class cannonMock(trajectory.Cannon): #Unrendered mock of cannon class
        def __init__(self):
                    print "Initializing cannon"
                    self._targets = []
                    self.inclination = 0
                    self.azimuth = 180
                    self.aof = 180
                    self.rof = 10
                    self.vel = 3
                    self.ang = 180
                    self.height = 0
                    self.hits = []
                    self.projectiles = []
                    self.center = [0, 0]
                    self.fireTrigger = pygame.MEDFIRE
                    self.shotRequested = False
                    self.projectile_radius = 2
                    self.range = 50
    
    
    def setUp(self):
        pass
    
    def testProjectileInitialization(self):
        C = self.cannonMock()
        P = trajectory.Physics()
        C.fire_projectile(trajectory.Cannonball, P)
        self.assertEqual(len(C.projectiles), 1, "Projectile information not appended to self.projectiles")
        self.assertIsInstance(C.projectiles[0], trajectory.Projectile, "Projectile[0] not an instance of trajectory.Projectile")
        
    def testProjectileInitialConditionPassing(self):
        C = self.cannonMock()
        P = trajectory.Physics()
        C.fire_projectile(trajectory.Cannonball, P)
        actual = C.projectiles[0].r_set[0]
        expected = np.array([[C.center[0], C.center[1], C.height], [C.vel*sin(C.inclination)*cos(C.azimuth), C.vel*sin(C.inclination)*sin(C.azimuth), C.vel*cos(C.inclination)]])
        i_count = 0
        for i in expected:
            j_count = 0
            for j in i:
                self.assertAlmostEqual(j, actual[i_count, j_count], 1, "Error setting cannon initial conditions in coordinates %s, %s" % (i_count, j_count))
                j_count += 1
            i_count += 1
        
    def testProjectileUpdate(self):
        C = self.cannonMock()
        P = trajectory.Physics()
        C.fire_projectile(trajectory.Cannonball, P)
        test_projectile = C.projectiles[0]
        expected = np.array(test_projectile.r_set[test_projectile.current_frame])
        test_projectile.frame_step()
        actual = np.array(test_projectile.r_set[test_projectile.current_frame])
        self.assertFalse(np.array(expected == actual).all(), "Updated frame is identical to previous frame")
        for i in range(2):
            for j in range(3):    
                self.assertAlmostEqual(actual[i,j], test_projectile.r_set[1][i,j], "Data from update frame not equal to frame[0 + 1]")
                
    def testHitDetection(self):
        C = self.cannonMock()
        P = trajectory.Physics()
        C.fire_projectile(trajectory.Cannonball, P)
        test_projectile = C.projectiles[0]
        test_projectile.set_initial_conditions([0,0,0], 0, pi/4, 20)
        while test_projectile.hit_status == False:
            test_projectile.frame_step()
        expected = test_projectile.r_set[-1]
        actual = test_projectile.r_set[test_projectile.current_frame]
        for i in range(2):
            for j in range(3):
                self.assertAlmostEqual(expected[i,j], actual[i,j], "Hit status not triggering on final frame")
                
        
    
    
    
    
        

        
        
        
        
        
            
        
    
    
        
        
    
    